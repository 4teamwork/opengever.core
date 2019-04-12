from datetime import datetime
from opengever.base.command import CreateDocumentCommand
from opengever.base.security import elevated_privileges
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import IDossierJournalPDFMarker
from opengever.document.interfaces import IDossierTasksPDFMarker
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATE_RESOLVED
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import IDossierResolver
from opengever.dossier.resolve_lock import ResolveLock
from opengever.task.task import ITask
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
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


NOT_SUPPLIED_OBJECTS = _(
    "not all documents and tasks are stored in a subdossier.")
NOT_CHECKED_IN_DOCS = _("not all documents are checked in")
NOT_CLOSED_TASKS = _("not all task are closed")
NO_START_DATE = _("the dossier start date is missing.")
MSG_ACTIVE_PROPOSALS = _("The dossier contains active proposals.")


def get_resolver(dossier):
    """Return the currently configured dossier-resolver."""

    resolver_name = api.portal.get_registry_record(
        'resolver_name', IDossierResolveProperties)
    return getAdapter(dossier, IDossierResolver, name=resolver_name)


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

    def after_transition_hook(self, transition, disable_sync, transition_params):
        AfterResolveJobs(self.context).execute()


class DossierResolveView(BrowserView):

    def __call__(self):
        # Ensure already resolved dossier can't be resolved again
        if self.is_already_resolved():
            return self.show_already_resolved_msg()

        resolve_lock = ResolveLock(self.context)

        # Check whether a resolve is already in progress
        if resolve_lock.is_locked():
            resolve_lock.log('Concurrent attempt at resolving %s rejected' % self.context)
            return self.show_being_resolved_msg()

        # No resolve in progress, proceed with resolving this dossier
        # by acquring a lock, resolving, and then releasing the lock
        try:
            resolve_lock.acquire(commit=True)
            result = self.execute_recursive_resolve()

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

    def execute_recursive_resolve(self):
        resolver = get_resolver(self.context)

        # check preconditions
        errors = resolver.get_precondition_violations()
        if errors:
            return self.show_errors(errors)

        # validate enddates
        invalid_dates = resolver.are_enddates_valid()
        if invalid_dates:
            return self.show_invalid_end_dates(titles=invalid_dates)

        if resolver.is_archive_form_needed():
            return self.redirect('transition-archive')

        resolver.resolve()

        if self.context.is_subdossier():
            return self.show_subdossier_resolved_msg()

        return self.show_dossier_resolved_msg()

    @property
    def context_url(self):
        return self.context.absolute_url()

    def is_already_resolved(self):
        wfstate = api.content.get_state(obj=self.context)
        return wfstate == DOSSIER_STATE_RESOLVED

    def redirect(self, url):
        return self.request.RESPONSE.redirect(url)

    def show_already_resolved_msg(self):
        api.portal.show_message(
            message=_('Dossier has already been resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_being_resolved_msg(self):
        api.portal.show_message(
            message=_('Dossier is already being resolved'),
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_errors(self, errors):
        for msg in errors:
            api.portal.show_message(
                message=msg, request=self.request, type='error')
        return self.redirect(self.context_url)

    def show_invalid_end_dates(self, titles):
        for title in titles:
            msg = _("The dossier ${dossier} has a invalid end_date",
                    mapping=dict(dossier=title,))
            api.portal.show_message(
                message=msg, request=self.request, type='error')
        return self.redirect(self.context_url)

    def show_subdossier_resolved_msg(self):
        api.portal.show_message(
            message=_('The subdossier has been succesfully resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_dossier_resolved_msg(self):
        api.portal.show_message(
            message=_('The dossier has been succesfully resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)


class DossierReactivateView(BrowserView):

    def __call__(self):
        ptool = getToolByName(self, 'plone_utils')

        resolver = get_resolver(self.context)

        # check preconditions
        if resolver.is_reactivate_possible():
            resolver.reactivate()
            ptool.addPortalMessage(_('Dossiers successfully reactivated.'),
                                   type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            ptool.addPortalMessage(
                _("It isn't possible to reactivate a sub dossier."),
                type="warning")
            self.request.RESPONSE.redirect(self.context.absolute_url())


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

    def get_precondition_violations(self):
        """Check whether all preconditions are fulfilled.

        Return a list of errors, or an empty list when resolving is possible.
        """
        errors = ResolveConditions(
            self.context, self.strict).check_preconditions()

        if not errors:
            self.preconditions_fulfilled = True
        return errors

    def are_enddates_valid(self):
        """Check if the end dates of dossiers and subdossiers are valid.
        Return a list of objs with a invalid date,
        when it's empty everything is valid.
        """
        errors = ResolveConditions(self.context).check_end_dates()

        if not errors:
            self.enddates_valid = True
        return errors

    def is_archive_form_needed(self):

        if not IFilingNumberMarker.providedBy(self.context):
            return False

        if self.context.is_subdossier():
            return False
        else:
            return True

    def resolve(self, end_date=None):
        if not self.enddates_valid or not self.preconditions_fulfilled:
            raise TypeError

        elif self.is_archive_form_needed() and not end_date:
            raise TypeError
        else:
            Resolver(self.context).resolve_dossier(end_date=end_date)

    def is_reactivate_possible(self):
        parent = self.context.get_parent_dossier()
        if parent:
            wft = getToolByName(self.context, 'portal_workflow')
            if wft.getInfoFor(parent,
                              'review_state') not in DOSSIER_STATES_OPEN:
                return False
        return True

    def reactivate(self):
        if not self.is_reactivate_possible():
            raise TypeError
        Reactivator(self.context).reactivate_dossier()


class AfterResolveJobs(object):
    """Tasks that need to be executed after resolving a dossier.
    """

    def __init__(self, context):
        self.context = context

    def get_property(self, name):
        return api.portal.get_registry_record(
            name, interface=IDossierResolveProperties)

    def contains_tasks(self):
        tasks = api.content.find(
            context=self.context, depth=-1, object_provides=ITask)
        return len(tasks) > 0

    def execute(self):
        """After resolving a dossier, some cleanup jobs have to be executed:

        - Remove all shadowed documents.
        - Remove all trashed documents.
        - (Trigger PDF-A conversion).
        - Generate a PDF output of the journal.
        - For a main dossier, Generate a PDF listing the tasks.
        """

        self.trash_shadowed_docs()
        self.purge_trash()
        self.create_journal_pdf()
        if not self.context.is_subdossier() and self.contains_tasks():
            self.create_tasks_listing_pdf()
        self.trigger_pdf_conversion()

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

    def create_journal_pdf(self):
        """Creates a pdf representation of the dossier journal, and add it to
        the dossier as a normal document.

        If the dossiers has an end date use that date as the document date.
        This prevents the dossier from entering an invalid state with a
        document date outside the dossiers start-end range.
        """
        if not self.get_property('journal_pdf_enabled'):
            return

        view = self.context.unrestrictedTraverse('pdf-dossier-journal')
        today = api.portal.get_localized_time(
            datetime=datetime.today(), long_format=True)
        filename = u'Journal {}.pdf'.format(today)
        title = _(u'title_dossier_journal',
                  default=u'Journal of dossier ${title}, ${timestamp}',
                  mapping={'title': self.context.title,
                           'timestamp': today})
        kwargs = {
            'preserved_as_paper': False,
        }
        dossier = IDossier(self.context)
        if dossier and dossier.end:
            kwargs['document_date'] = dossier.end

        results = api.content.find(object_provides=IDossierJournalPDFMarker,
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
                interfaces=[IDossierJournalPDFMarker],
                **kwargs).execute()
            document.reindexObject(idxs=['object_provides'])

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

        docs = api.content.find(self.context, object_provides=[IBaseDocument])
        for doc in docs:
            ArchivalFileConverter(doc.getObject()).trigger_conversion()


class LenientDossierResolver(StrictDossierResolver):
    """The lenient dossier resolver does not enforce that documents and tasks
    are filed in subdossiers if the main dossier has subdossiers.
    """
    strict = False


class Resolver(object):

    def __init__(self, context):
        self.context = context
        self.wft = getToolByName(self.context, 'portal_workflow')

    def resolve_dossier(self, end_date=None):
        self._recursive_resolve(self.context, end_date)

    def _recursive_resolve(self, dossier, end_date, recursive=False):

        # no end_date is given use the earliest possible
        if not end_date:
            end_date = dossier.earliest_possible_end_date()

        if recursive:
            # check the subdossiers end date
            # If a subdossier is already resolved, but seems to have an invalid
            # end date, it's because we changed the resolution logic and rules
            # over time, and that subdossier's end date has retroactively become
            # invalid. In this case, we correct the end date according to current
            # rules and proceed with resolving it.
            if dossier.is_resolved() and not dossier.has_valid_enddate():
                IDossier(dossier).end = dossier.earliest_possible_end_date()
            # if no end date is set or the end_date is invalid, set to the parent
            # end date. Invalid end_date should normally be prevented by
            # ResolveConditions._recursive_date_validation, but this correction
            # would happen for example when resolving a dossier in debug mode.
            elif not IDossier(dossier).end or not dossier.has_valid_enddate():
                IDossier(dossier).end = end_date
        else:
            # main dossier set the given end_date
            IDossier(dossier).end = end_date
        dossier.reindexObject(idxs=['end'])

        for subdossier in dossier.get_subdossiers():
            self._recursive_resolve(
                subdossier.getObject(), end_date, recursive=True)

        if self.wft.getInfoFor(dossier,
                               'review_state') in DOSSIER_STATES_OPEN:
            self.wft.doActionFor(dossier, 'dossier-transition-resolve')


class Reactivator(object):

    def __init__(self, context):
        self.context = context
        self.wft = getToolByName(self.context, 'portal_workflow')

    def reactivate_dossier(self):
        self._recursive_reactivate(self.context)

    def _recursive_reactivate(self, dossier):
        for subdossier in dossier.get_subdossiers():
            self._recursive_reactivate(subdossier.getObject())

        if self.wft.getInfoFor(dossier,
                               'review_state') == 'dossier-state-resolved':

            self.reset_end_date(dossier)
            self.wft.doActionFor(dossier, 'dossier-transition-reactivate')

    def reset_end_date(self, dossier):
        IDossier(dossier).end = None
        dossier.reindexObject(idxs=['end'])


class ResolveConditions(object):

    def __init__(self, context, strict=True):
        self.context = context
        self.strict = strict

    def check_preconditions(self):
        """Check if all preconditions are fulfilled:
         - all_supplied
         - all checked in
         - all closed
        """

        errors = []

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
        if not self.context.has_valid_startdate():
            errors.append(NO_START_DATE)

        return errors

    def check_end_dates(self):
        """Recursively check if the dossier has a valid end date."""

        self._invalid_dates = []
        self._recursive_date_validation(self.context)

        return self._invalid_dates

    def _recursive_date_validation(self, dossier, main=True):

        if not main:
            # check end_date
            # If a dossier is already resolved, but seems to have an invalid
            # end date, it's because we changed the resolution logic and rules
            # over time, and that subdossier's end date has retroactively become
            # invalid. In this case, should allow the resolving the main dossier
            # anyway, and correct the invalid end date during dossier resolution.
            if not dossier.is_resolved() and not dossier.has_valid_enddate():
                self._invalid_dates.append(dossier.title)

        # recursively check subdossiers
        subdossiers = dossier.get_subdossiers()
        for sub in subdossiers:
            sub = sub.getObject()
            self._recursive_date_validation(sub, main=False)
