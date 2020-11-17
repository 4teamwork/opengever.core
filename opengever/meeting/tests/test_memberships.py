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
from opengever.meeting.wrapper import MemberWrapper
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase


class TestPathBar(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_committee_member_cant_see_membership_edit_links(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee_participant_1)

        table = browser.css('#membership_listing').first
        self.assertEqual(
            [[u'Rechnungspr\xfcfungskommission',
              'Jan 01, 2014', 'Dec 31, 2016', '']],
            table.lists())


class TestMemberships(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMemberships, self).setUp()
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .with_default_period()
                                .within(self.container))
        self.member = create(Builder('member').having(
            admin_unit_id=self._admin_unit_id)
        )
        self.member_wrapper = MemberWrapper.wrap(self.container, self.member)

        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeAdministrator', 'CommitteeResponsible')

    def test_get_url(self):
        membership = create(Builder('membership').having(
            committee=self.committee.load_model(), member=self.member))

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/membership-1',
            membership.get_url(self.committee))

    @browsing
    def test_membership_can_be_added(self, browser):
        self.assertEqual(0, len(self.committee.get_memberships()))

        browser.login().open(self.committee, view='add-membership')

        browser.fill({'Start date': '01.01.2010',
                      'End date': '31.12.2010',
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
        browser.fill({'Start date': '01.01.2010',
                      'End date': '31.12.2010',
                      'Member': str(self.member.member_id)}).submit()

        browser.open(self.committee, view='add-membership')
        browser.fill({'Start date': '01.06.2010',
                      'End date': '31.12.2010',
                      'Member': str(self.member.member_id)}).submit()

        # portal messages
        self.assertEqual(['There were some errors.'], error_messages())
        # form field error
        self.assertEqual(
            ["Can't add membership, it overlaps an existing membership from "
             "Jan 01, 2010 to Dec 31, 2010."],
            browser.css('div#content-core div.error').text)

    @browsing
    def test_site_title_is_membership_title(self, browser):
        membership = create(Builder('membership')
                            .having(member=self.member,
                                    committee=self.committee.load_model(),
                                    date_from=date(2003, 01, 01),
                                    date_to=date(2007, 12, 31)))

        browser.login().open(membership.get_edit_url())
        self.assertEquals(
            u'M\xfcller Peter, Jan 01, 2003 - Dec 31, 2007 \u2014 Plone site',
            browser.css('title').first.text)

    @browsing
    def test_membership_can_be_edited(self, browser):
        membership = create(Builder('membership')
                            .having(member=self.member,
                                    committee=self.committee.load_model(),
                                    date_from=date(2003, 01, 01),
                                    date_to=date(2007, 12, 31)))

        browser.login().open(membership.get_edit_url())
        browser.fill({'Role': u'tempor\xe4re Leitung',
                      'Start date': '31.12.2003'}).submit()

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

        browser.login().open(membership.get_edit_url())
        browser.fill({'Start date': '31.12.2005'}).submit()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertEqual(
            ["Can't change membership, it overlaps an existing membership from "
             "Jan 01, 2003 to Jan 01, 2007."],
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
