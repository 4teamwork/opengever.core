from opengever.testing import FunctionalTestCase
from ftw.testbrowser import browsing
from opengever.testing import create_ogds_user
from zExceptions import NotFound


class TestUserDetails(FunctionalTestCase):

    @browsing
    def test_user_details(self, browser):
        create_ogds_user('hugo.boss', lastname='Boss', firstname='Hugo',
                         groups=('group_a', 'group_b'))

        browser.open(self.portal, view='@@user-details/hugo.boss')

        self.assertEquals(['Boss Hugo (hugo.boss)'],
                          browser.css('h1.documentFirstHeading').text)
        self.assertEquals(['group_a', 'group_b'],
                          browser.css('.groups a').text)

    @browsing
    def test_user_details_return_not_found_for_not_exisiting_user(self, browser):
        with self.assertRaises(NotFound):
            browser.open(self.portal, view='@@user-details/hugo.boss')
