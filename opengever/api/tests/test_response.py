from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.response import COMMENT_RESPONSE_TYPE
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
        self.assertEqual([], browser.json['responses'])

        # Dossier
        browser.open(self.dossier, method="GET", headers=self.api_headers)
        self.assertEqual([], browser.json['responses'])

        # Document
        self.login(self.regular_user, browser=browser)
        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertNotIn('responses', browser.json)

    @browsing
    def test_returns_list_of_serialized_response_objects(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = u'Ich bin hier anderer Meinung!'
            IResponseContainer(self.todo).add(response)

        with freeze(datetime(2016, 12, 24, 8, 23)):
            with self.login(self.workspace_admin):
                response = Response()
                response.text = u'Ok, Danke f\xfcr dein Feedback'
                response.add_change('title', 'Foo', 'Bar')
                IResponseContainer(self.todo).add(response)

        browser.open(self.todo, method="GET", headers=self.api_headers)
        self.assertEquals(
            [{u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1/@responses/1481272800000000',
              u'changes': [],
              u'created': u'2016-12-09T09:40:00',
              u'creator': {
                  u'title': u'Schr\xf6dinger B\xe9atrice',
                  u'token': u'beatrice.schrodinger'},
              u'modified': None,
              u'modifier': None,
              u'additional_data':{},
              u'response_id': 1481272800000000,
              u'response_type': u'default',
              u'text': u'Ich bin hier anderer Meinung!',
              },
             {u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1/@responses/1482564180000000',
              u'changes': [{u'after': u'Bar',
                            u'before': u'Foo',
                            u'field_id': u'title',
                            u'field_title': u''}],
              u'created': u'2016-12-24T08:23:00',
              u'creator': {
                  u'title': u'Hugentobler Fridolin',
                  u'token': u'fridolin.hugentobler'},
              u'modified': None,
              u'modifier': None,
              u'additional_data':{},
              u'response_id': 1482564180000000,
              u'response_type': u'default',
              u'text': u'Ok, Danke f\xfcr dein Feedback',
              }
             ],
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
            response = Response()
            response.text = u'Ich bin hier anderer Meinung!'
            IResponseContainer(self.todo).add(response)

        url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
        browser.open(url, method="GET", headers=self.api_headers)
        self.assertEquals(
            {u'@id': url,
             u'changes': [],
             u'created': u'2016-12-09T09:40:00',
             u'creator': {u'title': u'Schr\xf6dinger B\xe9atrice',
                          u'token': self.workspace_member.id},
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'response_id': 1481272800000000,
             u'response_type': u'default',
             u'text': u'Ich bin hier anderer Meinung!',
             },
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
             'response_id': 1481272800000000,
             'response_type': 'comment',
             u'created': u'2016-12-09T09:40:00',
             u'changes': [],
             u'creator': {
                 u'token': self.workspace_member.id,
                 u'title': u'Schr\xf6dinger B\xe9atrice'},
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'text': u'Angebot \xfcberpr\xfcft',
             },
            browser.json)

    @browsing
    def test_add_response_to_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assertEqual([], IResponseContainer(self.dossier).list())

        with freeze(datetime(2016, 12, 9, 9, 40)):
            browser.open(self.dossier, view='@responses', method="POST", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        responses = IResponseContainer(self.dossier).list()
        self.assertEqual(1, len(responses))
        self.assertEqual(u'Angebot \xfcberpr\xfcft', responses[0].text)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                     u'dossier-1/@responses/1481272800000000',
             u'changes': [],
             u'created': u'2016-12-09T09:40:00',
             u'creator': {u'title': u'B\xe4rfuss K\xe4thi', u'token': self.regular_user.id},
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'response_id': 1481272800000000,
             u'response_type': u'comment',
             u'text': u'Angebot \xfcberpr\xfcft'}, browser.json)

    @browsing
    def test_data_is_validated(self, browser):
        self.login(self.workspace_member, browser=browser)

        url = '{}/@responses'.format(self.todo.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, method="POST", headers=self.api_headers)

        self.assertEquals(
            {u'message': u"Property 'text' is required", u'type': u'BadRequest'},
            browser.json)


class TestResponsePatch(IntegrationTestCase):

    @browsing
    def test_edit_a_response_requires_edit_permission(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(Response())

        with browser.expect_http_error(401):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="PATCH", headers=self.api_headers,
                         data=json.dumps({'text': 'test'}))

    @browsing
    def test_edit_a_response_sucessful(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = 'Test'
            response.response_type = COMMENT_RESPONSE_TYPE
            IResponseContainer(self.todo).add(response)

        url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
        self.login(self.workspace_member, browser=browser)
        with freeze(datetime(2018, 10, 10, 9, 15)):
            browser.open(url, method="PATCH", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        responses = IResponseContainer(self.todo).list()
        self.assertEqual(1, len(responses))
        self.assertEqual(u'Angebot \xfcberpr\xfcft', responses[0].text)
        self.assertEqual(self.workspace_member.getId(), responses[0].modifier)
        self.assertEqual(datetime(2018, 10, 10, 9, 15), responses[0].modified)

        self.assertEquals(204, browser.status_code)

    @browsing
    def test_data_is_validated(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = 'Test'
            response.response_type = COMMENT_RESPONSE_TYPE
            IResponseContainer(self.todo).add(response)
        with browser.expect_http_error(400):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="PATCH", headers=self.api_headers)

        self.assertEquals(
            {u'message': u"Property 'text' is required", u'type': u'BadRequest'},
            browser.json)
        self.assertEquals('Test', IResponseContainer(self.todo).list()[0].text)

    @browsing
    def test_cannot_edit_response_that_is_not_of_type_comment(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = 'Test'
            response.response_type = u'blah'
            IResponseContainer(self.todo).add(response)

        with browser.expect_http_error(400):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="PATCH", headers=self.api_headers,
                         data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        self.assertEqual({u'type': u'BadRequest', u'additional_metadata': {},
                          u'translated_message': u'Only responses of type "Comment" can be edited.',
                          u'message': u'only_comment_type_can_be_edited'}, browser.json)


class TestResponseDelete(IntegrationTestCase):

    @browsing
    def test_delete_a_response_requires_edit_permission(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            IResponseContainer(self.todo).add(Response())

        with browser.expect_http_error(401):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="DELETE", headers=self.api_headers)

    @browsing
    def test_delete_a_response_sucessful(self, browser):
        self.login(self.workspace_member, browser=browser)
        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = 'Test'
            response.response_type = COMMENT_RESPONSE_TYPE
            IResponseContainer(self.todo).add(response)

        self.assertEqual(1, len(IResponseContainer(self.todo).list()))

        url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
        browser.open(url, method="DELETE", headers=self.api_headers)

        self.assertEqual(0, len(IResponseContainer(self.todo).list()))

    @browsing
    def test_cannot_delete_response_that_is_not_of_type_comment(self, browser):
        self.login(self.workspace_member, browser=browser)

        with freeze(datetime(2016, 12, 9, 9, 40)):
            response = Response()
            response.text = 'Test'
            response.response_type = u'blah'
            IResponseContainer(self.todo).add(response)

        with browser.expect_http_error(400):
            url = '{}/@responses/1481272800000000'.format(self.todo.absolute_url())
            browser.open(url, method="DELETE", headers=self.api_headers)

        self.assertEqual({
            u'type': u'BadRequest', u'additional_metadata': {},
            u'translated_message': u'Only responses of type "Comment" can be deleted.',
            u'message': u'only_comment_type_can_be_deleted'}, browser.json)
