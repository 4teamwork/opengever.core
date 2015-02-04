from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Member
from opengever.testing import FunctionalTestCase


class TestMemberships(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMemberships, self).setUp()
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(self.container))
        self.member = create(Builder('member'))

    @browsing
    def test_membership_can_be_added(self, browser):
        self.assertEqual(0, len(self.committee.get_memberships()))

        browser.login().open(self.committee, view='add-membership')

        browser.fill({'Start date': '1/1/10',
                      'End date': '12/31/10',
                      'Member': str(self.member.member_id),
                      'Role': u'H\xe4nswurscht'}).submit()

        memberships = self.committee.get_memberships()
        self.assertEqual(1, len(memberships))

        membership = memberships[0]
        self.assertEqual(Member.get(self.member.member_id), membership.member)
        self.assertEqual(date(2010, 1, 1), membership.date_from)
        self.assertEqual(date(2010, 12, 31), membership.date_to)
        self.assertEqual(u'H\xe4nswurscht', membership.role)
