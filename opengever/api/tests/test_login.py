from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
import json


class TestLogin(IntegrationTestCase):

    @browsing
    def test_login_returns_jwt_by_default(self, browser):
        browser.open(
            self.portal.absolute_url() + '/@login',
            data=json.dumps({
                "login": TEST_USER_NAME,
                "password": TEST_USER_PASSWORD,
            }),
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'token', browser.json)

    @browsing
    def test_login_returns_ac_cookie_if_requested(self, browser):
        browser.open(
            self.portal.absolute_url() + '/@login',
            data=json.dumps({
                "login": TEST_USER_NAME,
                "password": TEST_USER_PASSWORD,
                "set_cookie": True,
            }),
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
        )
        self.assertEqual(browser.status_code, 200)
        self.assertIn(u'userid', browser.json)
        self.assertIn(u'__ac', browser.cookies)

    @browsing
    def test_login_fails_with_wrong_credentials(self, browser):
        with browser.expect_unauthorized():
            browser.open(
                self.portal.absolute_url() + '/@login',
                data=json.dumps({
                    "login": TEST_USER_NAME,
                    "password": 'wrong password',
                }),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )
