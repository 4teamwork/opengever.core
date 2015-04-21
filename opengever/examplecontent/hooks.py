from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import session
from opengever.base.model import create_session
from opengever.testing.builders.dx import *
from opengever.testing.builders.sql import *
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility


class MeetingExampleContentCreator(object):

    def __init__(self, site):
        self.site = site
        self.db_session = create_session()
        self.setup_builders()
        self.committee = self.site['sitzungen']['committee-1']
        self.committee_model = self.committee.load_model()

    def setup_builders(self):
        session.current_session = session.factory()
        session.current_session.session = self.db_session

    def create_content(self):
        self.create_members()

    def create_members(self):
        peter = create(Builder('member')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        hans = create(Builder('member')
                      .having(firstname=u'Hans', lastname=u'Meier'))

        create(Builder('membership')
               .having(committee=self.committee_model,
                       member=peter,
                       date_from=date.today(),
                       date_to=date.today() + timedelta(days=512)))

        create(Builder('membership')
               .having(committee=self.committee_model,
                       member=hans,
                       date_from=date.today(),
                       date_to=date.today() + timedelta(days=512)))


def block_portlets_for_meetings(site):
    content = site.restrictedTraverse('sitzungen')
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=content)

    # Block inherited context portlets on content
    assignable = getMultiAdapter(
        (content, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


def init_profile_installed(site):
    creator = MeetingExampleContentCreator(site)
    creator.create_content()

    block_portlets_for_meetings(site)
