from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import BadRequest
from zExceptions import NotFound


class TestGlobalSourcesGet(IntegrationTestCase):

    @browsing
    def test_globalsources_returns_a_list_of_all_globalsources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources'.format(self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            [{u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups',
              u'title': u'all_users_and_groups'}],
            browser.json)

    @browsing
    def test_raises_not_found_for_not_existing_sources(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/not-existing'.format(self.portal.absolute_url())

        with browser.expect_http_error(404):
            browser.open(url, headers=self.api_headers)

    @browsing
    def test_raises_bad_request_when_try_to_enumerate_source(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/all_users_and_groups'.format(
            self.portal.absolute_url())

        with browser.expect_http_error(400):
            browser.open(url, headers=self.api_headers)

    @browsing
    def test_returns_batched_results(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@globalsources/all_users_and_groups?query=Rober'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalsources/all_users_and_groups?query=Rober',
             u'items': [{u'title': u'Ziegler Robert (robert.ziegler)',
                         u'token': u'robert.ziegler'}],
             u'items_total': 1},
            browser.json)
