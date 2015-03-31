from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.members import MemberView
from opengever.meeting.model import Member
from opengever.testing import FunctionalTestCase
from pyquery import PyQuery


class TestMemberListing(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMemberListing, self).setUp()
        self.container = create(Builder('committee_container'))
        self.member = create(Builder('member'))

    @browsing
    def test_members_can_be_added_in_browser(self, browser):
        browser.login().open(self.container, view='add-member')
        browser.fill({'Firstname': u'Hanspeter',
                      'Lastname': u'Hansj\xf6rg',
                      'E-Mail': u'foo@example.com'}).submit()
        self.assertEquals([u'Record created'], info_messages())

        hans = Member.query.filter_by(firstname=u'Hanspeter').first()
        self.assertEqual(MemberView.url_for(self.container, hans),
                         browser.url)

        self.assertIsNotNone(hans)
        self.assertEqual(u'Hanspeter', hans.firstname)
        self.assertEqual(u'Hansj\xf6rg', hans.lastname)
        self.assertEqual(u'foo@example.com', hans.email)

    @browsing
    def test_memers_can_be_edited_in_browser(self, browser):
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
            'http://nohost/plone/opengever-meeting-committeecontainer/member/1',
            link.get('href'))
        self.assertEqual('contenttype-opengever-meeting-member', link.get('class'))
        self.assertEqual('Peter Meier', link.get('title'))
        self.assertEqual('Peter Meier', link.text)
