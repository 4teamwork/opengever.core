from datetime import datetime
from opengever.base.command import CreateDocumentCommand
from opengever.base.security import elevated_privileges
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import IDossierTasksPDFMarker
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.exceptions import PreconditionsViolated
from opengever.dossier.filing.form import IFilingFormSchema
from opengever.dossier.interfaces import IDossierArchiver
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import IDossierResolver
from opengever.dossier.resolve_lock import ResolveLock
from opengever.dossier.statusmessage_mixin import DossierResolutionStatusmessageMixin
from opengever.task.task import ITask
from plone import api
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getSiteManager
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import transaction


MAIN_DOSSIER_NOT_ACTIVE = _("Dossier is not active and cannot be resolved.")
NOT_SUPPLIED_OBJECTS = _(
    "not all documents and tasks are stored in a subdossier.")
NOT_CHECKED_IN_DOCS = _("not all documents are checked in")
NOT_CLOSED_TASKS = _("not all task are closed")
NO_START_DATE = _("the dossier start date is missing.")
MSG_ACTIVE_PROPOSALS = _("The dossier contains active proposals.")
MSG_ACTIVE_WORKSPACES = _("Not all linked workspaces are deactivated.")
MSG_CONTAINS_WORKSPACE_WITHOUT_VIEW_PERMISSION = _(
    u"Not all linked workspaces are accessible by the current user.")
MSG_ALREADY_BEING_RESOLVED = _("Dossier is already being resolved")

AFTER_RESOLVE_JOBS_PENDING_KEY = 'opengever.dossier.resolve.after_resolve_jobs_pending'


class AlreadyBeingResolved(Exception):
    """A concurrent attempt at resolving a dossier was made.
    """


class InvalidDates(Exception):
    """One or more dossier dates are invalid.
    """

    def __init__(self, invalid_dossier_titles):
        self.invalid_dossier_titles = invalid_dossier_titles


def get_resolver(dossier):
    """Return the currently configured dossier-resolver."""

    resolver_name = api.portal.get_registry_record(
        'resolver_name', IDossierResolveProperties)
    return getAdapter(dossier, IDossierResolver, name=resolver_name)


def is_archive_form_needed(dossier):

    if not IFilingNumberMarker.providedBy(dossier):
        return False

    if dossier.is_subdossier():
        return False
    else:
        return True


class ValidResolverNamesVocabularyFactory(object):
    """Return a vocabulary that contains the names of all named-adapters
    registered as IDossierResolver for IDossierMarker.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        sitemanager = getSiteManager()
        resolver_adapter_names = sitemanager.adapters.names(
            [IDossierMarker], IDossierResolver)
        return SimpleVocabulary.fromValues(resolver_adapter_names)


@implementer(ITransitionExtender)
@adapter(IDossierMarker, IBrowserRequest)
class ResolveDossierTransitionExtender(TransitionExtender):
    """TransitionExtender that gets invoked when resolving dossiers.
    """

    @property
    def schemas(self):
        if IFilingNumberMarker.providedBy(self.context) and \
           not self.context.is_subdossier():

            return [IFilingFormSchema]

        return []

    def after_transition_hook(self, transition, disable_sync, transition_params):
        AfterResolveJobs(self.context).execute()
        self.execute_custom_after_transition_hook(transition, transition_params)

    def execute_custom_after_transition_hook(self, transition, transition_params):
        custom_after_transition_hook = api.portal.get_registry_record(
            'resolver_custom_after_transition_hook', IDossierResolveProperties)

        if not custom_after_transition_hook:
            return

        portal = api.portal.get()
        ec = createExprContext(folder=self.context, portal=portal, object=self.context)
        expr = Expression(custom_after_transition_hook)
        expr(ec)


class LockingResolveManager(object):
    """Recursively resolves a dossier and uses a persistent resolve lock.

    Will raise PreconditionsViolated or InvalidDates exceptions if the
    necessary preconditions are not satisfied.

    If a persistent lock exists and another resolve attempt is made, an
    AlreadyBeingResolved exception will be raised.
    """

    def __init__(self, context):
        self.context = context
        self.resolver = get_resolver(self.context)

    def resolve(self, **transition_params):
        resolve_lock = ResolveLock(self.context)

        # Check whether a resolve is already in progress
        if resolve_lock.is_locked():
            resolve_lock.log('Concurrent attempt at resolving %s rejected' % self.context)
            raise AlreadyBeingResolved

        # No resolve in progress, proceed with resolving this dossier
        # by acquring a lock, resolving, and then releasing the lock
        try:
            resolve_lock.acquire(commit=True)
            auto_close_tasks = transition_params.get("auto_close_tasks", False)
            if auto_close_tasks:
                pending_tasks = self._get_pending_tasks()
                self._auto_close_tasks(pending_tasks)

            result = self.execute_recursive_resolve(**transition_params)

            # We need to commit here so that a possible ConflictError already
            # manifests here, in our try..finally that will remove the lock.
            # Otherwise the ConflictError would happen when *trying* to remove
            # the lock (and commit), which would fail and leave us with a left
            # over lock which would cause the retried request to be rejected.
            transaction.commit()
            resolve_lock.log('Successfully resolved %s' % self.context)
            return result

        except Exception:
            transaction.abort()
            raise

        finally:
            # We end up here in three cases:
            #
            # 1) Resolve was successful (no exception)
            #
            # 2) A ConflictError happened during the commit() above. We then
            #    remove the lock here, and are ready for the request to be
            #    retried, once the ConflictError continues to be propagated.
            #
            # 3) An exception happened during resolve, and the txn has been
            #    aborted just above (but the exception has not been
            #    propagated yet).
            #
            # In either case, we remove the lock and commit the removal. If
            # there was an exception, propagation will continue after leaving
            # this 'finally' block.
            resolve_lock.release(commit=True)

    def _auto_close_tasks(self, tasks):
        """Auto-close all pending tasks."""
        for brain in tasks:
            task = brain.getObject()
            task.force_finish_task()

    def _get_pending_tasks(self):
        """Get all pending tasks in dossier."""
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        return catalog.searchResults(
            path=path,
            object_provides=ITask.__identifier__,
            is_subtask=False,
            review_state=['task-state-open', 'task-state-in-progress', 'task-state-resolved']
        )

    def execute_recursive_resolve(self, **transition_params):
        self.resolver.raise_on_failed_preconditions()
        if is_archive_form_needed(self.context):
            IDossierArchiver(self.context).run(**transition_params)

        self.resolver.resolve(
            end_date=transition_params.get('dossier_enddate'), **transition_params)


class DossierResolveView(BrowserView, DossierResolutionStatusmessageMixin):

    def __call__(self):
        # Ensure already resolved dossier can't be resolved again
        if self.is_already_resolved():
            return self.show_already_resolved_msg()

        resolve_manager = LockingResolveManager(self.context)

        # If filing number feature is enabled, we redirect to an additional
        # archive form that needs to be filled out first. The actual resolving
        # will then be triggered from that form.
        if is_archive_form_needed(self.context):
            # Validate preconditions early. This is so we don't redirect to the
            # archive form (if filing number feature enabled) in a case where
            # it will fail anyway because of violated preconditions.
            #
            # XXX: This will validate preconditions *thrice* though (the second
            # time in the archiv form and then via resolve_manager.resolve()).
            # This should eventually be cleaned up so we don't unnecessarily
            # validate preconditions multiple times.
            try:
                resolve_manager.resolver.raise_on_failed_preconditions()

            except PreconditionsViolated as exc:
                return self.show_errors(exc.errors)

            except InvalidDates as exc:
                return self.show_invalid_end_dates(titles=exc.invalid_dossier_titles)

            archive_url = '/'.join((self.context_url, 'transition-archive'))
            return self.redirect(archive_url)

        try:
            resolve_manager.resolve()

        except PreconditionsViolated as exc:
            return self.show_errors(exc.errors)

        except InvalidDates as exc:
            return self.show_invalid_end_dates(titles=exc.invalid_dossier_titles)

        except AlreadyBeingResolved:
            return self.show_being_resolved_msg()

        # Success
        if self.context.is_subdossier():
            return self.show_subdossier_resolved_msg()

        return self.show_dossier_resolved_msg()

    def is_already_resolved(self):
        return self.context.is_resolved()


@implementer(IDossierResolver)
@adapter(IDossierMarker)
class StrictDossierResolver(object):
    """The strict dossier resolver enforces that documents and tasks
    are filed in subdossiers if the dossier contains at least one subdossier.
    """
    preconditions_fulfilled = False
    enddates_valid = False
    strict = True

    def __init__(self, context):
        self.context = context
        self.wft = getToolByName(self.context, 'portal_workflow')

    def get_precondition_violations(self):
        """Check whether all preconditions are fulfilled.

        Return a list of errors, or an empty list when resolving is possible.
        """
        errors = ResolveConditions(
            self.context, self.strict).check_preconditions()

        if not errors:
            self.preconditions_fulfilled = True
        return errors

    def raise_on_failed_preconditions(self):
        """Verify preconditions, and raise respective exceptions if violated.
        """
        # check preconditions
        errors = self.get_precondition_violations()
        if errors:
            raise PreconditionsViolated(errors=errors)

        # validate enddates
        invalid_dates = self.are_enddates_valid()
        if invalid_dates:
            raise InvalidDates(invalid_dossier_titles=invalid_dates)

    def are_enddates_valid(self):
        """Check if the end dates of dossiers and subdossiers are valid.
        Return a list of objs with a invalid date,
        when it's empty everything is valid.
        """
        errors = ResolveConditions(self.context).check_end_dates()

        if not errors:
            self.enddates_valid = True
        return errors

    def resolve(self, end_date=None, auto_close_tasks=False, **kwargs):
        if not self.enddates_valid or not self.preconditions_fulfilled:
            raise TypeError

        elif is_archive_form_needed(self.context) and not end_date:
            raise TypeError

        end_date = end_date or self.context.earliest_possible_end_date()
        self._recursive_resolve(
            self.context, end_date, triggering_dossier=True, **kwargs)

    def _recursive_resolve(self, dossier, end_date, triggering_dossier=False, **kwargs):
        new_end_date = None

        if triggering_dossier:
            new_end_date = end_date
        else:
            # check the subdossiers end date
            # If a subdossier is already resolved, but seems to have an invalid
            # end date, it's because we changed the resolution logic and rules
            # over time, and that subdossier's end date has retroactively become
            # invalid. In this case, we correct the end date according to current
            # rules and proceed with resolving it.
            if dossier.is_resolved() and not dossier.has_valid_enddate():
                new_end_date = dossier.earliest_possible_end_date()
            # if no end date is set or the end_date is invalid, set to the parent
            # end date. Invalid end_date should normally be prevented by
            # ResolveConditions._recursive_date_validation, but this correction
            # would happen for example when resolving a dossier in debug mode.
            elif not IDossier(dossier).end or not dossier.has_valid_enddate():
                new_end_date = end_date

        if new_end_date:
            IDossier(dossier).end = new_end_date
            dossier.reindexObject(idxs=['end'])

        for subdossier in dossier.get_subdossiers(
                depth=1, sort_on=None, sort_order=None):
            self._recursive_resolve(
                subdossier.getObject(), end_date, triggering_dossier=False, **kwargs)

        if dossier.is_open():
            self.wft.doActionFor(dossier, 'dossier-transition-resolve', transition_params=kwargs)


class AfterResolveJobs(object):
    """Tasks that need to be executed after resolving a dossier.
    """

    def __init__(self, context):
        self.context = context
        self.catalog = api.portal.get_tool('portal_catalog')
        self.num_pdf_conversions = 0

    def get_property(self, name):
        return api.portal.get_registry_record(
            name, interface=IDossierResolveProperties)

    def contains_tasks(self):
        path = '/'.join(self.context.getPhysicalPath())
        tasks = self.catalog.unrestrictedSearchResults(
            path=path,
            object_provides=ITask.__identifier__)
        return len(tasks) > 0

    def execute(self, nightly_run=False):
        """After resolving a dossier, some cleanup jobs have to be executed:

        - Remove all shadowed documents.
        - Remove all trashed documents.
        - (Trigger PDF-A conversion).
        - For a main dossier, Generate a PDF listing the tasks.

        If the feature for nightly jobs is enabled (via registry), we skip
        these during normal operation during the day (nightly_run=False), and
        the following night this method will be invoked by a nightly job
        (with nightly_run=True) to finally perform these jobs.
        """
        if not nightly_run:
            # Defer execution of after resolve jobs to a nightly job
            self.after_resolve_jobs_pending = True
            return

        self.trash_shadowed_docs()
        self.purge_trash()
        if not self.context.is_subdossier() and self.contains_tasks():
            self.create_tasks_listing_pdf()
        self.trigger_pdf_conversion()
        self.after_resolve_jobs_pending = False

    @property
    def after_resolve_jobs_pending(self):
        """This flag tracks whether these jobs have already been executed for
        a resolved dossier, or are still pending (because they have been
        deferred to a nightly job).
        """
        ann = IAnnotations(self.context)
        return ann.get(AFTER_RESOLVE_JOBS_PENDING_KEY, False)

    @after_resolve_jobs_pending.setter
    def after_resolve_jobs_pending(self, value):
        assert isinstance(value, bool)
        ann = IAnnotations(self.context)
        ann[AFTER_RESOLVE_JOBS_PENDING_KEY] = value
        self.context.reindexObject(idxs=['after_resolve_jobs_pending'])

    def trash_shadowed_docs(self):
        """Trash all documents that are in shadow state (recursive).
        """
        portal_catalog = api.portal.get_tool('portal_catalog')
        query = {'path': {'query': self.context.absolute_url_path(), 'depth': -1},
                 'object_provides': [IBaseDocument.__identifier__],
                 'review_state': "document-state-shadow"}
        shadowed_docs = portal_catalog.unrestrictedSearchResults(query)

        if shadowed_docs:
            with elevated_privileges():
                api.content.delete(
                    objects=[brain.getObject() for brain in shadowed_docs])

    def purge_trash(self):
        """Delete all trashed documents inside the dossier (recursive).
        """
        if not self.get_property('purge_trash_enabled'):
            return

        trashed_docs = api.content.find(
            context=self.context,
            depth=-1,
            object_provides=[IBaseDocument],
            trashed=True)

        if trashed_docs:
            with elevated_privileges():
                api.content.delete(
                    objects=[brain.getObject() for brain in trashed_docs])

    def create_tasks_listing_pdf(self):
        """Creates a pdf representation of the dossier tasks, and add it to
        the dossier as a normal document.

        If the dossiers has an end date use that date as the document date.
        This prevents the dossier from entering an invalid state with a
        document date outside the dossiers start-end range.
        """
        if not self.get_property('tasks_pdf_enabled'):
            return

        view = self.context.unrestrictedTraverse('pdf-dossier-tasks')

        today = api.portal.get_localized_time(
            datetime=datetime.today(), long_format=True)
        filename = u'Tasks {}.pdf'.format(today)
        title = _(u'title_dossier_tasks',
                  default=u'Task list of dossier ${title}, ${timestamp}',
                  mapping={'title': self.context.title,
                           'timestamp': today})
        kwargs = {
            'preserved_as_paper': False,
        }
        dossier = IDossier(self.context)
        if dossier and dossier.end:
            kwargs['document_date'] = dossier.end

        results = api.content.find(object_provides=IDossierTasksPDFMarker,
                                   depth=1,
                                   context=self.context)

        with elevated_privileges():
            if len(results) > 0:
                document = results[0].getObject()
                document.title = translate(title, context=self.context.REQUEST)
                comment = _(u'Updated with a newer generated version from dossier ${title}.',
                            mapping=dict(title=self.context.title))
                document.update_file(view.get_data(), create_version=True,
                                     comment=comment)
                return

            document = CreateDocumentCommand(
                self.context, filename, view.get_data(),
                title=translate(title, context=self.context.REQUEST),
                content_type='application/pdf',
                interfaces=[IDossierTasksPDFMarker],
                **kwargs).execute()
            document.reindexObject(idxs=['object_provides'])

    def trigger_pdf_conversion(self):
        if not self.get_property('archival_file_conversion_enabled'):
            return

        for doc in self.context.get_contained_documents(unrestricted=True):
            self.num_pdf_conversions += ArchivalFileConverter(
                doc.getObject()).trigger_conversion()


class LenientDossierResolver(StrictDossierResolver):
    """The lenient dossier resolver does not enforce that documents and tasks
    are filed in subdossiers if the main dossier has subdossiers.
    """
    strict = False


class ResolveConditions(object):

    def __init__(self, context, strict=True):
        self.context = context
        self.strict = strict

    def check_preconditions(self):
        """Check if all preconditions are fulfilled:
         - main dossier is in an open state
         - all_supplied
         - all checked in
         - all closed
        """

        errors = []
        if not self.context.is_open():
            errors.append(MAIN_DOSSIER_NOT_ACTIVE)
        if (self.strict
                and not self.context.is_subdossier()
                and not self.context.is_all_supplied()):
            errors.append(NOT_SUPPLIED_OBJECTS)
        if not self.context.is_all_checked_in():
            errors.append(NOT_CHECKED_IN_DOCS)
        if self.context.has_active_tasks():
            errors.append(NOT_CLOSED_TASKS)
        if self.context.has_active_proposals():
            errors.append(MSG_ACTIVE_PROPOSALS)
        if self.context.is_linked_to_active_workspaces():
            errors.append(MSG_ACTIVE_WORKSPACES)
        if self.context.has_linked_workspaces_without_view_permission():
            errors.append(MSG_CONTAINS_WORKSPACE_WITHOUT_VIEW_PERMISSION)
        if not self.context.has_valid_startdate():
            errors.append(NO_START_DATE)

        if not self.check_custom_precondition():
            errors.append(api.portal.get_registry_record(
                'resolver_custom_precondition_error_text_de', IDossierResolveProperties))

        return errors

    def check_custom_precondition(self):
        resolver_custom_precondition = api.portal.get_registry_record(
            'resolver_custom_precondition', IDossierResolveProperties)

        if not resolver_custom_precondition:
            return True

        portal = api.portal.get()
        ec = createExprContext(folder=self.context, portal=portal, object=self.context)
        expr = Expression(resolver_custom_precondition)
        return expr(ec)

    def check_end_dates(self):
        """Recursively check if the dossier has a valid end date."""

        self._invalid_dates = []
        self._recursive_date_validation(self.context)

        return self._invalid_dates

    def _recursive_date_validation(self, dossier):
        # When the archive form is needed on a dossier, we need not check the
        # end date as it will be set in the form.
        if not is_archive_form_needed(dossier):
            # check end_date
            # If a dossier is already resolved, but seems to have an invalid
            # end date, it's because we changed the resolution logic and rules
            # over time, and that subdossier's end date has retroactively become
            # invalid. In this case, should allow the resolving the main dossier
            # anyway, and correct the invalid end date during dossier resolution.
            if not dossier.is_resolved() and not dossier.has_valid_enddate():
                self._invalid_dates.append(dossier.title)

        # recursively check subdossiers
        subdossiers = dossier.get_subdossiers(depth=1)
        for sub in subdossiers:
            sub = sub.getObject()
            self._recursive_date_validation(sub)
