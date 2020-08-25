from copy import copy
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from urllib import urlencode
import json
import requests_mock


class TestRemoteWorkflowPost(IntegrationTestCase):

    def setup_remote_admin_unit(self, remote_admin_unit_name='remote'):
        create(
            Builder('admin_unit')
            .id(remote_admin_unit_name)
            .having(site_url='http://nohost/{}'.format(remote_admin_unit_name))
        )

    def prep_remote_task(self):
        """Prepare the SQL task corresponding to self.task in a way that
        tricks the @remote-workflow endpoint into thinking it's remote, and
        therefore doing a remote request.
        """
        sql_task = self.task.get_sql_object()
        sql_task.admin_unit_id = u'remote'
        return sql_task

    def construct_url_pair(self, sql_task, **kwargs):
        query_string = urlencode(kwargs, doseq=True)
        remote_url = '/'.join((
            'http://nohost',
            sql_task.admin_unit_id,
            sql_task.physical_path,
            '@workflow', 'some-transition'))

        local_url = '/'.join((
            self.portal.absolute_url(),
            '@remote-workflow', 'some-transition'))

        if query_string:
            remote_url = '?'.join((remote_url, query_string))
            local_url = '?'.join((local_url, query_string))

        return remote_url, local_url

    @browsing
    def test_invoking_remote_workflow_requires_view_permisson(self, browser):
        url = '{}/@remote-workflow'.format(self.portal.absolute_url())

        # Merely invoking the endpoint requires View on the site root.
        # The required permission checks on the remote side will then
        # be performed as usual, the endpoint just proxies the request
        # in the security context of the user.
        with browser.expect_http_error(code=401):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    def test_requires_remote_oguid_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@remote-workflow'.format(self.portal.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Required parameter "remote_oguid" is missing in body'},
            browser.json)

    @browsing
    def test_gracefully_wraps_remote_non_json_responses(self, browser):
        self.setup_remote_admin_unit()
        self.login(self.regular_user, browser)
        sql_task = self.prep_remote_task()

        expected_remote_url, local_url = self.construct_url_pair(sql_task)

        with requests_mock.Mocker() as remote_server_mock:
            remote_server_mock.register_uri(
                'POST',
                expected_remote_url,
                status_code=500,
                headers={'Content-Type': 'application/maybe_json_maybe_not'},
                text="Here's some plain text")

            with browser.expect_http_error(500):
                browser.open(
                    local_url, method='POST',
                    data=json.dumps({'remote_oguid': 'remote:%s' % sql_task.int_id}),
                    headers=self.api_headers)

        self.assertEqual(
            {u'type': u'ValueError',
             u'message': u'Remote side returned a non-JSON response',
             u'remote_response_body': u"Here's some plain text"},
            browser.json)

        self.assertEqual('application/json', browser.headers['Content-Type'])

    @browsing
    def test_requires_valid_remote_oguid(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@remote-workflow'.format(self.portal.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'remote_oguid': 'i_am_malformed'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'MalformedOguid: i_am_malformed'},
            browser.json)

    @browsing
    def test_requires_oguid_that_refers_to_remote_object(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@remote-workflow'.format(self.portal.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'remote_oguid': 'plone:1234'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'NonRemoteOguid: Not a remote OGUID. Use get_url() instead'},
            browser.json)

    @browsing
    def test_remote_workflow_proxies_query_string_parameteres_to_remote(self, browser):
        self.setup_remote_admin_unit()
        self.login(self.regular_user, browser)
        sql_task = self.prep_remote_task()

        expected_response = {'this would be': 'the proxied response data'}
        expected_remote_url, local_url = self.construct_url_pair(
            sql_task, someparam=['foo', 'bar'])

        self.assertIn('someparam=foo&someparam=bar', expected_remote_url)

        with requests_mock.Mocker() as remote_server_mock:
            remote_server_mock.register_uri(
                'POST',
                expected_remote_url,
                status_code=200,
                json=expected_response)

            browser.open(
                local_url, method='POST',
                data=json.dumps({'remote_oguid': 'remote:%s' % sql_task.int_id}),
                headers=self.api_headers)

            self.assertEqual(expected_response, browser.json)

    @browsing
    def test_remote_workflow_proxies_remote_response(self, browser):
        self.setup_remote_admin_unit()
        self.login(self.regular_user, browser)
        sql_task = self.prep_remote_task()

        expected_remote_url, local_url = self.construct_url_pair(sql_task)
        expected_response = {'this would be': 'the proxied response data'}

        with requests_mock.Mocker() as remote_server_mock:
            remote_server_mock.register_uri(
                'POST',
                expected_remote_url,
                status_code=200,
                json=expected_response)

            browser.open(
                local_url, method='POST',
                data=json.dumps({'remote_oguid': 'remote:%s' % sql_task.int_id}),
                headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(expected_response, browser.json)
        self.assertEqual(
            expected_remote_url,
            browser.headers['X-GEVER-RemoteRequest'])

    @browsing
    def test_remote_workflow_proxies_status_line_and_body(self, browser):
        self.setup_remote_admin_unit()
        self.login(self.regular_user, browser)
        sql_task = self.prep_remote_task()

        expected_remote_url, local_url = self.construct_url_pair(sql_task)
        expected_status = 507
        expected_reason = 'Boom'
        expected_body = {'justification': 'Something went wrong'}

        with requests_mock.Mocker() as remote_server_mock:
            remote_server_mock.register_uri(
                'POST',
                expected_remote_url,
                status_code=expected_status,
                reason=expected_reason,
                json=expected_body)

            with browser.expect_http_error(expected_status):
                browser.open(
                    local_url, method='POST',
                    data=json.dumps({'remote_oguid': 'remote:%s' % sql_task.int_id}),
                    headers=self.api_headers)

        self.assertEqual(expected_status, browser.status_code)
        self.assertEqual(expected_reason, browser.status_reason)
        self.assertEqual(expected_body, browser.json)
        self.assertEqual(
            expected_remote_url,
            browser.headers['X-GEVER-RemoteRequest'])

    @browsing
    def test_remote_workflow_breaks_proxying_cycles(self, browser):
        self.setup_remote_admin_unit()
        self.login(self.regular_user, browser)
        sql_task = self.prep_remote_task()

        expected_remote_url, local_url = self.construct_url_pair(sql_task)

        with browser.expect_http_error(500):
            headers = copy(self.api_headers)
            headers['X-GEVER-RemoteRequestFrom'] = 'http://nohost/foo/'

            browser.open(
                local_url, method='POST',
                data=json.dumps({'remote_oguid': 'remote:%s' % sql_task.int_id}),
                headers=headers)

        self.assertEqual(500, browser.status_code)
        self.assertEqual(
            {u'message': u'Trying to proxy a request to %s, although the '
                         u'request was already proxied '
                         u'from http://nohost/foo/' % expected_remote_url,
             u'type': u'InternalError'},
            browser.json)
