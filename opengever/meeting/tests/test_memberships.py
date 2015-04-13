from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
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

        self.assertEquals([u'Record created'], info_messages())

        memberships = self.committee.get_memberships()
        self.assertEqual(1, len(memberships))

        membership = memberships[0]
        self.assertEqual(Member.get(self.member.member_id), membership.member)
        self.assertEqual(date(2010, 1, 1), membership.date_from)
        self.assertEqual(date(2010, 12, 31), membership.date_to)
        self.assertEqual(u'H\xe4nswurscht', membership.role)

    @browsing
    def test_no_overlapping_memberships_can_be_added(self, browser):
        browser.login().open(self.committee, view='add-membership')
        browser.fill({'Start date': '1/1/10',
                      'End date': '12/31/10',
                      'Member': str(self.member.member_id)}).submit()

        browser.open(self.committee, view='add-membership')
        browser.fill({'Start date': '6/1/10',
                      'End date': '12/31/10',
                      'Member': str(self.member.member_id)}).submit()

        # portal messages
        self.assertEqual(['There were some errors.'], error_messages())
        # form field error
        self.assertEqual(
            ["Can't add membership, it overlaps an existing membership from "
             "Jan 01, 2010 to Dec 31, 2010"],
            browser.css('div#content-core div.error').text)

    @browsing
    def test_membership_can_be_edited(self, browser):
        membership = create(Builder('membership')
                            .having(member=self.member,
                                    committee=self.committee.load_model(),
                                    date_from=date(2003, 01, 01),
                                    date_to=date(2007, 12, 31)))

        browser.login().open(membership.get_edit_url(self.committee))
        browser.fill({'Role': u'tempor\xe4re Leitung',
                      'Start date': 'December 31, 2003'}).submit()

        membership = Membership.get(membership.membership_id)
        self.assertEqual(['Changes saved'], info_messages())
        self.assertEqual(date(2003, 12, 31), membership.date_from)
        self.assertEqual(u'tempor\xe4re Leitung', membership.role)

    @browsing
    def test_overlapping_membership_not_possible_when_editing(self, browser):
        create(Builder('membership')
               .having(member=self.member,
                       committee=self.committee.load_model(),
                       date_from=date(2003, 01, 01),
                       date_to=date(2007, 01, 01)))
        membership = create(Builder('membership')
                            .having(member=self.member,
                                    committee=self.committee.load_model(),
                                    date_from=date(2008, 01, 01),
                                    date_to=date(2014, 01, 01)))

        browser.login().open(membership.get_edit_url(self.committee))
        browser.fill({'Start date': 'December 31, 2005'}).submit()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertEqual(
            ["Can't change membership, it overlaps an existing membership from "
             "Jan 01, 2003 to Jan 01, 2007"],
            browser.css('div#content-core div.error').text)

    def test_not_started_membership_is_inactive(self):
        create(Builder('membership')
               .having(member=self.member,
                       committee=self.committee.load_model(),
                       date_from=date.today() + timedelta(days=1),
                       date_to=date.today() + timedelta(days=100)))

        self.assertEquals([],
                          Membership.query.only_active().all())

    def test_already_finished_membership_is_inactive(self):
        create(Builder('membership')
               .having(member=self.member,
                       committee=self.committee.load_model(),
                       date_from=date.today() - timedelta(days=100),
                       date_to=date.today() - timedelta(days=1)))

        self.assertEquals([],
                          Membership.query.only_active().all())

    def test_actual_membership_is_active(self):
        membership = create(Builder('membership')
               .having(member=self.member,
                       committee=self.committee.load_model(),
                       date_from=date.today() - timedelta(days=1),
                       date_to=date.today() + timedelta(days=1)))

        self.assertEquals([membership],
                          Membership.query.only_active().all())
