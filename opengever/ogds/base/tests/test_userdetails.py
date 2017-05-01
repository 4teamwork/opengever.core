from opengever.testing import FunctionalTestCase
from ftw.testbrowser import browsing
from opengever.testing import create_ogds_user


class TestUserDetails(FunctionalTestCase):

    @browsing
    def test_user_details(self, browser):
        create_ogds_user('hugo.boss', lastname='Boss', firstname='Hugo',
                         groups=('group_a', 'group_b'))

        browser.login().open(self.portal, view='@@user-details/hugo.boss')

        self.assertEquals(['Boss Hugo (hugo.boss)'],
                          browser.css('h1.documentFirstHeading').text)
        self.assertEquals(['group_a', 'group_b'],
                          browser.css('.groups a').text)

    @browsing
    def test_user_details_return_not_found_for_not_exisiting_user(self, browser):
        with browser.expect_http_error(reason='Not Found'):
            browser.login().open(self.portal, view='@@user-details/hugo.boss')
