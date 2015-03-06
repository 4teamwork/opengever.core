from five import grok
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.interfaces import IDossierResolver
from Products.CMFCore.utils import getToolByName


NOT_SUPPLIED_OBJECTS = _(
    "not all documents and tasks are stored in a subdossier")
NOT_CHECKED_IN_DOCS = _("not all documents are checked in")
NOT_CLOSED_TASKS = _("not all task are closed")
NO_START_DATE = _("the dossier start date is missing.")


class DossierResolveView(grok.View):

    grok.context(IDossierMarker)
    grok.name('transition-resolve')
    grok.require('zope2.View')

    def render(self):

        ptool = getToolByName(self, 'plone_utils')

        resolver = IDossierResolver(self.context)

        # check preconditions
        errors = resolver.is_resolve_possible()
        if errors:
            for msg in errors:
                ptool.addPortalMessage(msg, type="error")

            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        # validate enddates
        invalid_dates = resolver.are_enddates_valid()
        if invalid_dates:
            for title in invalid_dates:
                ptool.addPortalMessage(
                    _("The dossier ${dossier} has a invalid end_date",
                      mapping=dict(dossier=title,)),
                    type="error")

            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        if resolver.is_archive_form_needed():
            self.request.RESPONSE.redirect('transition-archive')
        else:
            resolver.resolve()
            if self.context.is_subdossier():
                ptool.addPortalMessage(
                    _('The subdossier has been succesfully resolved'),
                    type='info')
            else:
                ptool.addPortalMessage(
                    _('The dossier has been succesfully resolved'),
                    type='info')

            self.request.RESPONSE.redirect(self.context.absolute_url())


class DossierReactivateView(grok.View):
    grok.context(IDossierMarker)
    grok.name('transition-reactivate')
    grok.require('zope2.View')

    def render(self):
        ptool = getToolByName(self, 'plone_utils')

        resolver = IDossierResolver(self.context)

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


class DossierResolver(grok.Adapter):
    grok.implements(IDossierResolver)
    grok.context(IDossierMarker)

    preconditions_fulfilled = False
    enddates_valid = False

    def is_resolve_possible(self):
        """Check if all preconditions are fulfilled.
        Return a list of errors, or a empty list when resolving is possible.
        """
        errors = ResolveConditions(self.context).check_preconditions()

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

            self.wft.doActionFor(dossier, 'dossier-transition-reactivate')


class ResolveConditions(object):

    def __init__(self, context):
        self.context = context

    def check_preconditions(self):
        """Check if all preconditions are fulfilled:
         - all_supplied
         - all checked in
         - all closed
        """

        errors = []

        if not self.context.is_all_supplied():
            errors.append(NOT_SUPPLIED_OBJECTS)
        if not self.context.is_all_checked_in():
            errors.append(NOT_CHECKED_IN_DOCS)
        if not self.context.is_all_closed():
            errors.append(NOT_CLOSED_TASKS)
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
