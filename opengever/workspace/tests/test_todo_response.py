from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.workspace.todos.content.response import IResponses
from opengever.workspace.todos.content.response import Response
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
        response.modifier = self.administrator.getId()
        self.assertEquals(self.administrator.getId(), response.modifier)


class TestResponses(IntegrationTestCase):

    def test_responses(self):
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
        browser.visit(self.todo, view='@responses')
        expected = {u"@id": self.todo_url + '/@responses',
                    u"items": []}

        self.assertEquals(expected, browser.json)

        with freeze(datetime(2010, 1, 2, 3, 4, 5)) as clock:
            IResponses(self.todo).append(Response(text=u'Response 1'))
            clock.forward(days=1)
            IResponses(self.todo).append(Response(text=u'Response 2'))

        expected = {u'@id': u'{}/@responses'.format(self.todo_url),
                    u'items': [
                        {u'creator': self.administrator.getId(),
                         u'text': u'Response 1',
                         u'created': u'2010-01-02T03:04:05',
                         u'modified': None,
                         u'modifier': None,
                         u'@id': u'{}/@responses/1'.format(self.todo_url),
                         u'id': 1},
                        {u'creator': self.administrator.getId(),
                         u'text': u'Response 2',
                         u'created': u'2010-01-03T03:04:05',
                         u'modified': None,
                         u'modifier': None,
                         u'@id': u'{}/@responses/2'.format(self.todo_url),
                         u'id': 2}]}

        browser.visit(self.todo, view='@responses')
        self.assertEquals(expected, browser.json)

    @browsing
    def test_get_response_by_id(self, browser):
        self.login(self.administrator, browser=browser)
        with freeze(datetime(2010, 1, 2, 3, 4, 5)) as clock:
            IResponses(self.todo).append(Response(text=u'Response 1'))
            clock.forward(days=1)
            IResponses(self.todo).append(Response(text=u'Response 2'))

        browser.replace_request_header('Accept', 'application/json')
        browser.visit(self.todo, view='@responses/2')

        self.assertEquals(
            {u'@id': u'{}/@responses/2'.format(self.todo_url),
             u'created': u'2010-01-03T03:04:05',
             u'creator': self.administrator.getId(),
             u'id': 2,
             u'modified': None,
             u'modifier': None,
             u'text': u'Response 2'},
            browser.json)

    @browsing
    def test_create_response(self, browser):
        with freeze(datetime(2010, 1, 2, 3, 4, 5)):
            self.login(self.administrator, browser=browser)
            browser.replace_request_header('Accept', 'application/json')
            browser.replace_request_header('Content-Type', 'application/json')
            browser.open(self.todo.absolute_url() + '/@responses',
                         method='POST',
                         data=json.dumps({
                             'text': 'A response'
                         }))

        self.assertEquals(
            {u'@id': u'{}/@responses/1'.format(self.todo_url),
             u'created': u'2010-01-02T03:04:05',
             u'creator': self.administrator.getId(),
             u'id': 1,
             u'modified': None,
             u'modifier': None,
             u'text': u'A response'},
            browser.json)

    @browsing
    def test_update_response(self, browser):
        self.login(self.administrator, browser=browser)
        response1 = Response(text=u'Response 1')
        IResponses(self.todo).append(response1)

        browser.replace_request_header('Accept', 'application/json')
        browser.replace_request_header('Content-Type', 'application/json')
        browser.open(self.todo.absolute_url() + '/@responses/1',
                     method='PATCH',
                     data=json.dumps({'text': 'Edited response'}))

        updated_response = IResponses(self.todo).all()[0]
        self.assertEquals('Edited response', updated_response.text)
        self.assertEquals(browser.json['modifier'], updated_response.modifier)
        self.assertEquals(browser.json['modified'],
                          json_compatible(updated_response.modified))

    @browsing
    def test_delete_response(self, browser):
        self.login(self.administrator, browser=browser)
        response1 = Response(text=u'Response 1')
        IResponses(self.todo).append(response1)

        browser.replace_request_header('Accept', 'application/json')
        browser.replace_request_header('Content-Type', 'application/json')
        browser.open(self.todo.absolute_url() + '/@responses/1',
                     method='DELETE')

        self.assertEquals(0, len(IResponses(self.todo).all()))
