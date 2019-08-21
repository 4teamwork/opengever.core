from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.testing import IntegrationTestCase
import json


class TestResponseGETSerialization(IntegrationTestCase):

    @browsing
    def test_get_contains_response_data_for_response_supported_content(self, browser):
        self.login(self.workspace_member, browser=browser)

        # Todo
        browser.open(self.todo, method="GET", headers=self.api_headers)
        self.assertEquals([], browser.json['responses'])

        # Document
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertNotIn('responses', browser.json)

    @browsing
    def test_returns_list_of_serialized_response_objects(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(
                Response('Ich bin hier anderer Meinung!'))

        with freeze(datetime(2016, 12, 24, 8, 23)):
            with self.login(self.workspace_admin):
                response = Response(u'Ok, Fanke f\xfcr dein Feedback')
                IResponseContainer(self.todo).add(response)

        browser.open(self.todo, method="GET", headers=self.api_headers)
        self.assertEquals(
            [{u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1/@responses/1481272800000000',
              u'created': u'2016-12-09T09:40:00',
              u'creator': self.workspace_member.id,
              u'text': u'Ich bin hier anderer Meinung!'},
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1/@responses/1482564180000000',
              u'created': u'2016-12-24T08:23:00',
              u'creator': self.workspace_admin.id,
              u'text': u'Ok, Fanke f\xfcr dein Feedback'}],
            browser.json['responses'])


class TestResponseGET(IntegrationTestCase):

    @browsing
    def test_raises_not_found_when_response_id_does_not_exist(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(404):
            url = '{}/@responses/111'.format(self.todo.absolute_url())
            browser.open(url, method="GET", headers=self.api_headers)

    @browsing
    def test_returns_the_serialized_response_object(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(
                Response('Ich bin hier anderer Meinung!'))

        url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
        browser.open(url, method="GET", headers=self.api_headers)

        self.assertEquals(
            {u'@id': url,
             u'created': u'2016-12-09T09:40:00',
             u'creator': self.workspace_member.id,
             u'text': u'Ich bin hier anderer Meinung!'},
            browser.json)


class TestResponsePost(IntegrationTestCase):

    @browsing
    def test_adding_a_response_requires_edit_permission(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with browser.expect_http_error(401):
            url = '{}/@responses'.format(self.todo.absolute_url())
            browser.open(url, method="POST", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

    @browsing
    def test_adding_a_response_sucessful(self, browser):
        self.login(self.workspace_member, browser=browser)

        self.assertEquals([], IResponseContainer(self.todo).list())

        with freeze(datetime(2016, 12, 9, 9, 40)):
            url = '{}/@responses'.format(self.todo.absolute_url())
            browser.open(url, method="POST", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        responses = IResponseContainer(self.todo).list()
        self.assertEquals(1, len(responses))
        self.assertEquals(u'Angebot \xfcberpr\xfcft', responses[0].text)

        self.assertEquals(201, browser.status_code)
        self.assertEquals(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1/@responses/1481272800000000',
             u'created': u'2016-12-09T09:40:00',
             u'creator': self.workspace_member.id,
             u'text': u'Angebot \xfcberpr\xfcft'},
            browser.json)

    @browsing
    def test_data_is_validated(self, browser):
        self.login(self.workspace_member, browser=browser)

        url = '{}/@responses'.format(self.todo.absolute_url())
        with browser.expect_http_error(500):
            browser.open(url, method="POST", headers=self.api_headers)

        self.assertEquals(
            {u'message': u'text', u'type': u'RequiredMissing'}, browser.json)


class TestResponsePatch(IntegrationTestCase):

    @browsing
    def test_edit_a_response_requires_edit_permission(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(Response('Test'))

        with browser.expect_http_error(401):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="PATCH", headers=self.api_headers,
                         data=json.dumps({'text': 'test'}))

    @browsing
    def test_edit_a_response_sucessful(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(Response('Test'))

        url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
        browser.open(url, method="PATCH", headers=self.api_headers,
                     data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        responses = IResponseContainer(self.todo).list()
        self.assertEquals(1, len(responses))
        self.assertEquals(u'Angebot \xfcberpr\xfcft', responses[0].text)

        self.assertEquals(204, browser.status_code)

    @browsing
    def test_data_is_validated(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(Response('Test'))

        with browser.expect_http_error(500):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="PATCH", headers=self.api_headers)

        self.assertEquals(
            {u'message': u'text', u'type': u'RequiredMissing'}, browser.json)
        self.assertEquals('Test', IResponseContainer(self.todo).list()[0].text)
