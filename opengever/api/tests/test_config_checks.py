from ftw.testbrowser import browsing
from opengever.base.tests.test_config_checks import DummyCheckMissconfigured1
from opengever.base.tests.test_config_checks import DummyCheckMissconfigured2
from opengever.testing import IntegrationTestCase
from zope.component import getSiteManager


class TestConfigChecks(IntegrationTestCase):

    @property
    def config_checks_url(self):
        return self.portal.absolute_url() + '/@config-checks'

    @browsing
    def test_endpoint_is_only_available_for_managers(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_http_error(401):
            browser.open(self.config_checks_url, headers=self.api_headers)

        self.login(self.manager, browser)
        browser.open(self.config_checks_url, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

    @browsing
    def test_response_with_no_errors(self, browser):
        self.login(self.manager, browser)
        browser.open(self.config_checks_url, headers=self.api_headers)
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/@config-checks',
                u'errors': []
            }, browser.json)

    @browsing
    def test_response_with_errors(self, browser):
        self.login(self.manager, browser)
        getSiteManager().registerAdapter(DummyCheckMissconfigured1, name="check-missconfigured-1")
        getSiteManager().registerAdapter(DummyCheckMissconfigured2, name="check-missconfigured-2")

        browser.open(self.config_checks_url, headers=self.api_headers)
        self.assertItemsEqual(
            {
                u'@id': u'http://nohost/plone/@config-checks',
                u'errors': [
                    {
                        u'description': u'Description 1',
                        u'id': u'DummyCheckMissconfigured1',
                        u'title': u'Dummy check 1'
                    },
                    {
                        u'description': u'',
                        u'id': u'DummyCheckMissconfigured2',
                        u'title': u'Dummy check 2'
                    }
                ]
            }, browser.json)
