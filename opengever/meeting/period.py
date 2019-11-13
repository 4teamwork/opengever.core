from opengever.meeting.exceptions import MultiplePeriodsFound
from plone import api
from plone.dexterity.content import Container
from plone.supermodel import model
import datetime


class IPeriod(model.Schema):
    """Marker interface for period."""


class Period(Container):

    @staticmethod
    def get_current(committee, date=None):
        """Return today's period for committe."""

        date = date or datetime.date.today()
        query = {
            'portal_type': 'opengever.meeting.period',
            'start': {'query': date, 'range': 'max'},
            'end': {'query': date, 'range': 'min'},
            'path': '/'.join(committee.getPhysicalPath()),
        }
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(query)

        if not brains:
            return None

        if len(brains) > 1:
            raise MultiplePeriodsFound()

        return brains[0].getObject()
