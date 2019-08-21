from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.response import IResponseContainer
from opengever.base.response import Response
from opengever.testing import IntegrationTestCase


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
