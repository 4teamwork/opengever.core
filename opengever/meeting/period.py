from opengever.meeting import _
from opengever.meeting.behaviors.period import IPeriodSchema
from opengever.meeting.exceptions import MultiplePeriodsFound
from plone import api
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form import util
from z3c.form import validator
from z3c.form.validator import InvariantsValidator
from zope.interface import Invalid
import datetime


class IPeriod(model.Schema):
    """Marker interface for period."""


class Period(Container):

    @staticmethod
    def get_current(committee, date=None, unrestricted=False):
        """Return today's period for committe."""

        start_date = date or datetime.date.today()

        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()

        query = {
            'portal_type': 'opengever.meeting.period',
            'start': {'query': start_date, 'range': 'max'},
            'end': {'query': start_date, 'range': 'min'},
            'path': '/'.join(committee.getPhysicalPath()),
        }

        catalog = api.portal.get_tool('portal_catalog')
        if unrestricted:
            brains = catalog.unrestrictedSearchResults(query)
        else:
            brains = catalog(query)

        if not brains:
            return None

        if len(brains) > 1:
            raise MultiplePeriodsFound()

        # if we are in restricted mode the initial catalog query will yield no
        # results if the user can't see the period.
        return api.portal.get().unrestrictedTraverse(brains[0].getPath())

    @property
    def extended_title(self):
        return u"{} ({} - {})".format(
            self.title,
            api.portal.get_localized_time(datetime=self.start),
            api.portal.get_localized_time(datetime=self.end))

    def get_next_decision_sequence_number(self):
        self.decision_sequence_number += 1
        return self.decision_sequence_number

    def get_next_meeting_sequence_number(self):
        self.meeting_sequence_number += 1
        return self.meeting_sequence_number


class PeriodValidator(InvariantsValidator):
    """Validates periods the following way:

    - Prevent that a committee has overlapping periods.
    - Make sure that end-date is before start-date
    """
    @staticmethod
    def get_overlapping_periods(committee, start, end, exclude=None):
        query = {
            'portal_type': 'opengever.meeting.period',
            'start': {'query': end, 'range': 'max'},
            'end': {'query': start, 'range': 'min'},
            'path': '/'.join(committee.getPhysicalPath()),
        }
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(query)

        if exclude:
            exclude_path = '/'.join(exclude.getPhysicalPath())
            brains = [each for each in brains
                      if each.getPath() != exclude_path]
        return brains

    def validateObject(self, obj):
        errors = super(PeriodValidator, self).validateObject(
            obj)

        committee = self.view.context
        start = obj.start
        end = obj.end

        exclude = None
        # if we are editing an existing period we should exclude it from
        # overlap detection.
        if IPeriod.providedBy(self.context):
            exclude = self.context

        overlapping = self.get_overlapping_periods(committee, start, end, exclude)
        if overlapping:
            errors += (Invalid(
                _(u"The period's range overlaps the following periods: "
                  "${periods}",
                mapping={'periods': u', '.join(
                    brain.Title for brain in overlapping)})),)

        if end < start:
            errors += (Invalid(
                _(u"The period's end date can't be before its start date.")),)

        return errors


validator.WidgetsValidatorDiscriminators(
    PeriodValidator,
    schema=util.getSpecification(IPeriodSchema, force=True))
