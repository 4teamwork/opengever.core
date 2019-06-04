from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.model import create_session
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Member
from opengever.meeting.wrapper import MemberWrapper
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from pyquery import PyQuery


class TestMember(IntegrationTestCase):

    def test_return_fullname_if_no_email(self):
        self.login(self.meeting_user)
        self.committee_president.model.email = None

        self.assertEqual(
            u'Sch\xf6ller Heidrun',
            self.committee_president.model.get_title())

    def test_return_linked_email_by_default(self):
        self.login(self.meeting_user)

        self.assertEqual(
            u'Sch\xf6ller Heidrun (<a href="mailto:h.schoeller@example.org">h.schoeller@example.org</a>)',
            self.committee_president.model.get_title())

    def test_return_unlinked_title_if_desired(self):
        self.login(self.meeting_user)

        self.assertEqual(
            u'Sch\xf6ller Heidrun (h.schoeller@example.org)',
            self.committee_president.model.get_title(show_email_as_link=False))

    def test_result_is_html_escaped(self):
        self.login(self.meeting_user)
        self.committee_president.model.lastname = u'<script></script>Sch\xf6ller'
        self.committee_president.model.email = None

        create_session().flush()  # the fullname property needs a nudge
        self.assertEqual(
            u'&lt;script&gt;&lt;/script&gt;Sch\xf6ller Heidrun',
            self.committee_president.model.get_title())


class TestMemberListing(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMemberListing, self).setUp()
        self.container = create(Builder('committee_container'))
        self.member = create(Builder('member'))

        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeAdministrator', 'CommitteeResponsible')

    @browsing
    def test_members_can_be_added_in_browser(self, browser):
        self.grant("Administrator", "CommitteeAdministrator")
        browser.login().open(self.container, view='add-member')
        browser.fill({'Firstname': u'Hanspeter',
                      'Lastname': u'Hansj\xf6rg',
                      'E-Mail': u'foo@example.com'}).submit()
        self.assertEquals([u'Record created'], info_messages())

        hans = Member.query.filter_by(firstname=u'Hanspeter').first()
        self.assertEqual('{}#members'.format(self.container.absolute_url()),
                         browser.url)

        self.assertIsNotNone(hans)
        self.assertEqual(u'Hanspeter', hans.firstname)
        self.assertEqual(u'Hansj\xf6rg', hans.lastname)
        self.assertEqual(u'foo@example.com', hans.email)

    @browsing
    def test_members_can_be_edited_in_browser(self, browser):
        browser.login()
        browser.open(self.member.get_edit_url(self.container))

        browser.fill({'Firstname': u'Hanspeter',
                      'Lastname': u'Hansj\xf6rg',
                      'E-Mail': u'foo@example.com'}).submit()

        self.assertEquals([u'Changes saved'], info_messages())

        member = Member.get(self.member.member_id)
        self.assertIsNotNone(member)
        self.assertEqual(u'Hanspeter', member.firstname)
        self.assertEqual(u'Hansj\xf6rg', member.lastname)
        self.assertEqual(u'foo@example.com', member.email)

    def test_member_link(self):
        link = self.member.get_link(self.container)
        link = PyQuery(link)[0]

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/member-1',
            link.get('href'))
        self.assertEqual('contenttype-opengever-meeting-member', link.get('class'))
        self.assertEqual(u'M\xfcller Peter', link.get('title'))
        self.assertEqual(u'M\xfcller Peter', link.text)


class TestMemberView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMemberView, self).setUp()
        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeAdministrator', 'CommitteeResponsible')

        self.container = create(Builder('committee_container'))
        self.member = create(Builder('member')
                             .having(email='p.meier@example.com'))
        self.member_wrapper = MemberWrapper.wrap(self.container, self.member)
        self.committee = create(Builder('committee')
                                .with_default_period()
                                .within(self.container))

        self.membership_1 = create(Builder('membership')
                                   .having(member=self.member,
                                           committee=self.committee.load_model(),
                                           role=u'Leitung',
                                           date_from=date(2008, 01, 01),
                                           date_to=date(2015, 01, 01)))

        self.membership_2 = create(Builder('membership')
                                   .having(member=self.member,
                                           committee=self.committee.load_model(),
                                           role=u'\xdcbungsleiter',
                                           date_from=date(2003, 01, 01),
                                           date_to=date(2007, 12, 31)))

    @browsing
    def test_site_title_is_member_title(self, browser):
        browser.login().open(self.member.get_url(self.container))
        self.assertEquals(
            u'M\xfcller Peter \u2014 Plone site',
            browser.css('title').first.text)

    @browsing
    def test_lists_member_properties(self, browser):
        browser.login().open(self.member.get_url(self.container))

        self.assertEqual(
            [['Lastname', u'M\xfcller'],
             ['Firstname', 'Peter'],
             ['E-Mail', 'p.meier@example.com']],
            browser.css('table#properties').first.lists())

    @browsing
    def test_show_message_if_member_has_no_memberships(self, browser):
        member = create(Builder('member'))
        browser.login().open(member.get_url(self.container))
        self.assertEqual(
            'This member has no memberships.',
            browser.css('#memberships span').first.text)

    @browsing
    def test_list_memberships(self, browser):
        browser.login().open(self.member.get_url(self.container))

        self.assertEqual(
            [['My Committee',
              'Jan 01, 2003',
              'Dec 31, 2007',
              u'\xdcbungsleiter',
              '',
              ''],
             ['My Committee',
              'Jan 01, 2008',
              'Jan 01, 2015',
              'Leitung',
              '',
              '']],
            browser.css('#membership_listing').first.lists())

    @browsing
    def test_committee_is_linked_correctly(self, browser):
        browser.login().open(self.member.get_url(self.container))
        row = browser.css('#membership_listing').first.rows[0]

        self.assertEqual(
            'http://example.com/opengever-meeting-committeecontainer/committee-1',
            row.css('td.committee a').first.get('href'))

    @browsing
    def test_edit_membership_is_linked_correctly(self, browser):
        browser.login().open(self.member.get_url(self.container))

        link = browser.css('a.edit_membership').first
        self.assertEqual(self.membership_2.get_edit_url(), link.get('href'))

    @browsing
    def test_remove_membership_link_is_correct(self, browser):
        browser.login().open(self.member.get_url(self.container))

        link = browser.css('a.remove_membership').first
        self.assertEqual(self.membership_2.get_remove_url(), link.get('href'))

    @browsing
    def test_remove_membership_works_correctly(self, browser):
        url = self.member.get_url(self.container)
        browser.login().open(url)
        self.assertEqual(2, len(browser.css('#membership_listing').first.rows))

        link = browser.css('a.remove_membership').first
        link.click()

        self.assertEqual(['The membership was deleted successfully.'],
                         info_messages())

        # I do not know why we need to reload. Feel free to fix this.
        browser.open(url)
        self.assertEqual(1, len(browser.css('#membership_listing').first.rows))
        self.assertEqual(['My Committee Jan 01, 2008 Jan 01, 2015 Leitung'],
                         browser.css('#membership_listing').first.rows.text)

        self.assertEqual(1, len(Member.query.first().memberships))
