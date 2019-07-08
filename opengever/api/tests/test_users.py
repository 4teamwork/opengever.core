from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import Unauthorized


class TestUsersGet(IntegrationTestCase):

    @browsing
    def test_enumarating_user_is_possible_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open('{}/@users'.format(self.portal.absolute_url()),
                     headers=self.api_headers)

        self.assertEquals(19, len(browser.json))

    @browsing
    def test_enumarating_users_unauthorized_raises(self, browser):
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open('{}/@users'.format(self.portal.absolute_url()),
                         headers=self.api_headers)
            self.assertEquals(19, len(browser.json))

    @browsing
    def test_accessing_an_other_user_is_possible_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@users/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.id)
        browser.open(url, headers=self.api_headers)

        self.assertEquals(
            {u'username': u'robert.ziegler',
             u'description': None,
             u'roles': [u'Member'],
             u'home_page': None,
             u'email': u'robert.ziegler@gever.local',
             u'location': None,
             u'portrait': None,
             u'fullname': u'Ziegler Robert',
             u'@id': u'http://nohost/plone/@users/robert.ziegler',
             u'id': u'robert.ziegler'}, browser.json)

    @browsing
    def test_unuathorized_accessing_an_other_user_raises(self, browser):
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            url = '{}/@users/{}'.format(
                self.portal.absolute_url(), self.dossier_responsible.id)
            browser.open(url, headers=self.api_headers)
