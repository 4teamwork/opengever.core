from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.content.response import IResponses
from opengever.workspace.todos.content.response import Response
from plone.app.testing import TEST_USER_ID
from plone.restapi.serializer.converters import json_compatible
import json


class TestToDoResponse(IntegrationTestCase):

    def setUp(self):
        super(TestToDoResponse, self).setUp()
        self.login(self.administrator)

    def test_created(self):
        with freeze(datetime(2010, 1, 1)):
            self.assertEquals(datetime.now(), Response(text=u'').created)

    def test_creator(self):
        self.assertEquals(self.administrator.getId(),
                          Response(text=u'').creator)

    def test_text(self):
        self.assertEquals(u'Ein Textli', Response(text=u'Ein Textli').text)

    def test_modifier(self):
        response = Response(text=u'')
        self.assertEquals(None, response.modifier)
        response.modifier = TEST_USER_ID
        self.assertEquals(TEST_USER_ID, response.modifier)


class TestResponses(IntegrationTestCase):

    def test_response(self):
        self.login(self.administrator)
        todo = create(Builder('todo'))
        self.assertEquals((), IResponses(todo).all())

        response1 = Response(text=u'Response 1')
        response2 = Response(text=u'Response 2')
        response3 = Response(text=u'Response 3')

        IResponses(todo).append(response1)
        IResponses(todo).append(response2)
        self.assertEquals((response1, response2), IResponses(todo).all())

        self.assertEquals(1, response1.id)
        self.assertEquals(2, response2.id)

        IResponses(todo).remove(response2)
        with self.assertRaises(ValueError):
            IResponses(todo).remove(response2)

        IResponses(todo).append(response3)
        self.assertEquals(3, response3.id)
        self.assertEquals((response1, response3), IResponses(todo).all())


class TestAPI(IntegrationTestCase):

    def setUp(self):
        super(TestAPI, self).setUp()
        self.login(self.administrator)
        container = create(Builder('todos container').within(self.workspace))
        self.todo = create(Builder('todo').within(container)
                           .titled(u'The ToDo'))

        self.todo_url = self.todo.absolute_url().decode('utf-8')

    @browsing
    def test_get_all_responses(self, browser):
        self.login(self.administrator, browser=browser)
        browser.replace_request_header('Accept', 'application/json')
        browser.visit(self.todo, view='@response')
        expected = [{u"@id": self.todo_url + '/@response',
                     u"responses": []}]

        self.assertEquals(expected, browser.json)

        response1 = Response(text=u'Response 1')
        response2 = Response(text=u'Response 2')
        IResponses(self.todo).append(response1)
        IResponses(self.todo).append(response2)

        expected = [{u"@id": self.todo_url + '/@response',
                     u"responses": map(lambda response: response.as_dict(),
                                       IResponses(self.todo).all())
                     }]

        browser.visit(self.todo, view='@response')
        self.assertEquals(expected, browser.json)

    @browsing
    def test_get_response_by_id(self, browser):
        response1 = Response(text=u'Response 1')
        response2 = Response(text=u'Response 2')
        IResponses(self.todo).append(response1)
        IResponses(self.todo).append(response2)

        self.login(self.administrator, browser=browser)
        browser.replace_request_header('Accept', 'application/json')
        browser.visit(self.todo, view='@response/1')

        self.assertEquals(response1.as_dict(), browser.json)

    @browsing
    def test_create_response(self, browser):
        self.login(self.administrator, browser=browser)
        browser.replace_request_header('Accept', 'application/json')
        browser.replace_request_header('Content-Type', 'application/json')
        browser.open(self.todo.absolute_url() + '/@response',
                     method='POST',
                     data=json.dumps({
                         'text': 'A response'
                     }))

        self.assertEquals(IResponses(self.todo).all()[0].as_dict(),
                          browser.json)

    @browsing
    def test_update_response(self, browser):
        response1 = Response(text=u'Response 1')
        IResponses(self.todo).append(response1)

        self.login(self.administrator, browser=browser)
        browser.replace_request_header('Accept', 'application/json')
        browser.replace_request_header('Content-Type', 'application/json')
        browser.open(self.todo.absolute_url() + '/@response',
                     method='PATCH',
                     data=json.dumps({
                         'text': 'Edited response',
                         'id': '1'
                     }))

        updated_response = IResponses(self.todo).all()[0]

        self.assertEquals('Edited response', updated_response.text)
        self.assertEquals(browser.json['modifier'], updated_response.modifier)
        self.assertEquals(browser.json['modified'],
                          json_compatible(updated_response.modified))

    @browsing
    def test_delete_response(self, browser):
        response1 = Response(text=u'Response 1')
        IResponses(self.todo).append(response1)

        self.login(self.administrator, browser=browser)
        browser.replace_request_header('Accept', 'application/json')
        browser.replace_request_header('Content-Type', 'application/json')
        browser.open(self.todo.absolute_url() + '/@response',
                     method='DELETE',
                     data=json.dumps({
                         'id': '1'
                     }))

        self.assertEquals(0, len(IResponses(self.todo).all()))
