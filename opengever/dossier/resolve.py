from datetime import datetime
from five import grok
from opengever.base.command import CreateDocumentCommand
from opengever.base.security import elevated_privileges
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.behaviors import IBaseDocument
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import IDossierResolver
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.component import getSiteManager
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


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


class DossierResolveView(grok.View):

    grok.context(IDossierMarker)
    grok.name('transition-resolve')
    grok.require('zope2.View')

    def render(self):
        resolver = get_resolver(self.context)

        # check preconditions
        errors = resolver.is_resolve_possible()
        if errors:
            for msg in errors:
                api.portal.show_message(
                    message=msg, request=self.request, type='error')

            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        # validate enddates
        invalid_dates = resolver.are_enddates_valid()
        if invalid_dates:
            for title in invalid_dates:
                msg = _("The dossier ${dossier} has a invalid end_date",
                        mapping=dict(dossier=title,))
                api.portal.show_message(
                    message=msg, request=self.request, type='error')

            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        if resolver.is_archive_form_needed():
            self.request.RESPONSE.redirect('transition-archive')
        else:
            resolver.resolve()
            if self.context.is_subdossier():
                api.portal.show_message(
                    message=_('The subdossier has been succesfully resolved.'),
                    request=self.request, type='info')
            else:
                api.portal.show_message(
                    message=_('The dossier has been succesfully resolved.'),
                    request=self.request, type='info')

            self.request.RESPONSE.redirect(self.context.absolute_url())


class DossierReactivateView(grok.View):
    grok.context(IDossierMarker)
    grok.name('transition-reactivate')
    grok.require('zope2.View')

    def render(self):
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


class StrictDossierResolver(grok.Adapter):
    """The strict dossier resolver enforces that documents and tasks
    are filed in subdossiers if the dossier contains at least one subdossier.
    """
    grok.implements(IDossierResolver)
    grok.context(IDossierMarker)
    grok.name('strict')

    preconditions_fulfilled = False
    enddates_valid = False
    strict = True

    def get_property(self, name):
        return api.portal.get_registry_record(
            name, interface=IDossierResolveProperties)

    def is_resolve_possible(self):
        """Check if all preconditions are fulfilled.
        Return a list of errors, or a empty list when resolving is possible.
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

    def after_resolve(self):
        """After resolving a dossier, some cleanup jobs have to be executed:

        - Remove all trashed documents.
        - (Trigger PDF-A conversion).
        - Generate a PDF output of the journal.
        """

        self.purge_trash()
        self.create_journal_pdf()
        self.trigger_pdf_conversion()

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

        with elevated_privileges():
            CreateDocumentCommand(
                self.context, filename, view.get_data(),
                title=translate(title, context=self.context.REQUEST),
                content_type='application/pdf',
                preserved_as_paper=False).execute()

    def trigger_pdf_conversion(self):
        if not self.get_property('archival_file_conversion_enabled'):
            return

        docs = api.content.find(self.context, object_provides=[IBaseDocument])
        for doc in docs:
            ArchivalFileConverter(doc.getObject()).trigger_conversion()

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


class LenientDossierResolver(StrictDossierResolver):
    """The lenient dossier resolver does not enforce that documents and tasks
    are filed in subdossiers if the main dossier has subdossiers.
    """
    grok.implements(IDossierResolver)
    grok.context(IDossierMarker)
    grok.name('lenient')

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
            # set the parent endate when no or a invalid end date is set
            if not IDossier(dossier).end or not dossier.has_valid_enddate():
                IDossier(dossier).end = end_date
        else:
            # main dossier set the given end_date
            IDossier(dossier).end = end_date

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

        if self.strict and not self.context.is_all_supplied():
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
            if not dossier.has_valid_enddate():
                self._invalid_dates.append(dossier.title)

        # recursively check subdossiers
        subdossiers = dossier.get_subdossiers()
        for sub in subdossiers:
            sub = sub.getObject()
            self._recursive_date_validation(sub, main=False)
