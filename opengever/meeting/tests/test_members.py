from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Member
from opengever.testing import FunctionalTestCase


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
        self.assertEqual(self.container.absolute_url(), browser.url)

        hans = Member.query.filter_by(firstname=u'Hanspeter').first()
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

        member = Member.get(self.member.member_id)
        self.assertIsNotNone(member)
        self.assertEqual(u'Hanspeter', member.firstname)
        self.assertEqual(u'Hansj\xf6rg', member.lastname)
        self.assertEqual(u'foo@example.com', member.email)
