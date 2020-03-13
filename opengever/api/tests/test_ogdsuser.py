from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest


class TestOGDSUserGet(IntegrationTestCase):

    @browsing
    def test_user_default_response(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.contactfolder,
                     view='@ogds-user/kathi.barfuss',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/kontakte/@ogds-user/kathi.barfuss',
             u'@type': u'virtual.ogds.user'},
            browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@ogds-user',
                         headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(self.contactfolder,
                         view='@ogds-user/kathi.barfuss/foobar',
                         headers=self.api_headers)
