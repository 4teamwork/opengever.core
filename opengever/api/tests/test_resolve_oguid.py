from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from urllib import urlencode
import json
import requests_mock


class TestResolveOguidGet(IntegrationTestCase):

    maxDiff = None

    def setup_remote_admin_unit(self, remote_admin_unit_name='remote'):
        create(
            Builder('admin_unit')
            .id(remote_admin_unit_name)
            .having(site_url='http://nohost/{}'.format(remote_admin_unit_name))
        )

    def get_resolve_urls(self, remote_unit='remote', int_id='1337', **kwargs):
        oguid = '{}:{}'.format(remote_unit, int_id)
        params = {
            'oguid': oguid,
        }
        params.update(**kwargs)
        query_string = urlencode(params)

        remote_url = 'http://nohost/{}/@resolve-oguid?{}'.format(
            remote_unit, query_string)
        local_url = '{}/@resolve-oguid?{}'.format(
            self.portal.absolute_url(), query_string)

        return remote_url, local_url

    @browsing
    def test_resolve_oguid_returns_serialized_object(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.task, method='GET', headers=self.api_headers)
        expected_task_json = browser.json

        url = '{}/@resolve-oguid?oguid={}'.format(
            self.portal.absolute_url(), str(Oguid.for_object(self.task)))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            expected_task_json, browser.json,
            "Response of GET to task url and resolution via @resolve-oguid "
            "should be equal.")

        self.assertDictContainsSubset(
            {u'@id': self.task.absolute_url(),
             u'@type': u'opengever.task.task',
             },
            browser.json
        )

    @browsing
    def test_resolve_oguid_respects_security(self, browser):
        self.login(self.administrator)
        oguid = Oguid.for_object(self.protected_document)

        self.login(self.regular_user, browser)
        url = '{}/@resolve-oguid?oguid={}'.format(self.portal.absolute_url(), str(oguid))

        with browser.expect_http_error(code=401):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_requires_oguid_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@resolve-oguid'.format(self.portal.absolute_url())

        with browser.expect_http_error(
                code=400, reason='Missing oguid query string parameter.'):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_requires_valid_oguid(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@resolve-oguid?oguid=qux'.format(self.portal.absolute_url())

        with browser.expect_http_error(
                code=400, reason='Malformed oguid "qux".'):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_requires_resolvable_oguid(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@resolve-oguid?oguid=plone:1234'.format(self.portal.absolute_url())

        with browser.expect_http_error(
                code=400, reason='No object found for oguid "plone:1234".'):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_requires_valid_admin_unit_id(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@resolve-oguid?oguid=qux:1234'.format(self.portal.absolute_url())

        with browser.expect_http_error(
                code=400, reason='Invalid admin unit id "qux".'):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_resolve_remote_oguid_proxies_remote_response(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            response = {'foo': 'bar'}
            mocker.get(remote_url, text=json.dumps(response))

            browser.open(local_url, method='GET', headers=self.api_headers)
            self.assertEqual(response, browser.json)

    @browsing
    def test_resolve_remote_oguid_proxies_query_string_parameteres_to_remote(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls(someparam='foo')
        self.assertIn('someparam=foo', remote_url)

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            response = {'qux': 1234}
            mocker.get(remote_url, text=json.dumps(response))

            browser.open(local_url, method='GET', headers=self.api_headers)
            self.assertEqual(response, browser.json)

    @browsing
    def test_remote_400_raises_local_400(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            mocker.get(remote_url, status_code=400)

            with browser.expect_http_error(400):
                browser.open(local_url, method='GET', headers=self.api_headers)

    @browsing
    def test_remote_404_raises_local_404(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            mocker.get(remote_url, status_code=404)

            with browser.expect_http_error(404):
                browser.open(local_url, method='GET', headers=self.api_headers)

    @browsing
    def test_remote_500_raises_local_500(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            mocker.get(remote_url, status_code=500)

            with browser.expect_http_error(500):
                browser.open(local_url, method='GET', headers=self.api_headers)

    @browsing
    def test_remote_502_raises_local_502(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            mocker.get(remote_url, status_code=502)

            with browser.expect_http_error(502):
                browser.open(local_url, method='GET', headers=self.api_headers)

    @browsing
    def test_remote_504_raises_local_504(self, browser):
        self.setup_remote_admin_unit()
        remote_url, local_url = self.get_resolve_urls()

        self.login(self.regular_user, browser)
        with requests_mock.Mocker() as mocker:
            mocker.get(remote_url, status_code=504)

            with browser.expect_http_error(504):
                browser.open(local_url, method='GET', headers=self.api_headers)
