from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from zope.component import getUtility
import json


class TestToDoList(IntegrationTestCase):

    @browsing
    def test_todolist_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('ToDo list')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Retrospektive'})
        form.save()

        assert_no_error_messages(browser)

        todolist = browser.context
        self.assertEqual('todolist-3', todolist.id)
        self.assertEqual('Retrospektive', todolist.title)

    @browsing
    def test_todos_are_addable_in_a_todolist(self, browser):
        self.login(self.workspace_member, browser)

        browser.visit(self.todolist_general)
        factoriesmenu.add('ToDo')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Bitte Vorbereitungen treffen.'})
        form.save()

        assert_no_error_messages(browser)
        todo, = self.todolist_general.objectValues()
        self.assertEqual(u'Bitte Vorbereitungen treffen.', todo.title)

    def test_todolist_is_searchable_by_title(self):
        self.login(self.workspace_member)
        self.assertItemsEqual(
            ['allgemeine', 'informationen'],
            index_data_for(self.todolist_general).get('SearchableText'))

    def test_todolist_uses_a_global_and_separate_sequencenumber_counter(self):
        self.login(self.workspace_member)
        sequence = getUtility(ISequenceNumber)

        self.assertEqual(1, sequence.get_number(self.todolist_general))
        self.assertEqual(2, sequence.get_number(self.todolist_introduction))

        todolist = create(Builder('todolist').titled(u'Konzeptphase'))
        self.assertEqual(3, sequence.get_number(todolist))

    def test_todolist_id_is_todolist_dash_and_sequence_number(self):
        self.login(self.workspace_member)

        self.assertEqual('todolist-1', self.todolist_general.id)
        self.assertEqual('todolist-2', self.todolist_introduction.id)

        todolist = create(Builder('todolist').titled(u'Konzeptphase'))
        self.assertEqual('todolist-3', todolist.id)


class TestAPISupportForTodoLists(IntegrationTestCase):

    @browsing
    def test_create(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({'title': 'Allgemeine Projektinformationen',
                             '@type': 'opengever.workspace.todolist'}))

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Allgemeine Projektinformationen',
                         browser.json['title'])
        self.assertEqual('todolist-3', browser.json['id'])

    @browsing
    def test_read(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(self.todolist_general, method='GET',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Allgemeine Informationen', browser.json['title'])
        self.assertEqual(u'opengever.workspace.todolist',
                         browser.json['@type'])
        self.assertEqual(u'opengever_workspace_todolist--STATUS--active',
                         browser.json['review_state'])

    @browsing
    def test_update(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(self.todolist_general, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xfcberarbeitungsphase'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xfcberarbeitungsphase',
                         self.todolist_general.title)

    @browsing
    def test_deletion_is_only_possible_for_empty_lists(self, browser):
        self.login(self.workspace_member, browser)

        # Not empty
        with browser.expect_http_error(500):
            browser.open(self.todolist_introduction, method='DELETE',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'The todolist is not empty, therefore deletion is not allowed.',
             u'type': u'ValueError'},
            browser.json)

        # empty
        list_id = self.todolist_general.id
        self.assertIn(list_id, self.workspace.objectIds())

        browser.open(self.todolist_general, method='DELETE',
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertNotIn(list_id, self.workspace.objectIds())

    @browsing
    def test_change_order_via_api(self, browser):
        self.login(self.workspace_admin, browser)

        create(Builder('todolist')
               .titled(u'Konzeptphase')
               .within(self.workspace))
        create(Builder('todolist')
               .titled(u'Dokumentationen')
               .within(self.workspace))

        self.assertEqual(
            ['folder-1', u'todolist-1', u'todolist-2',
             'opengever-workspace.todo', u'todolist-3', u'todolist-4'],
            self.workspace.objectIds())

        # change order
        data = {
            'ordering': {
                'obj_id': 'todolist-1',
                'delta': '2',
                'subset_ids': ['todolist-1', 'todolist-2', 'todolist-3',
                               'todolist-4']}}
        browser.open(self.workspace, method='PATCH',
                     headers=self.api_headers, data=json.dumps(data))

        self.assertEqual(
            ['folder-1', u'todolist-2', u'todolist-3',
             'opengever-workspace.todo', u'todolist-1', u'todolist-4'],
            self.workspace.objectIds())

    @browsing
    def test_only_order_change_is_allowed_for_workspace_member(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(self.workspace)
        # Updating title is not allowed
        data = {'title': 'New workspace title'}
        with browser.expect_http_error(401):
            browser.open(self.workspace, method='PATCH',
                         headers=self.api_headers, data=json.dumps(data))

        # Updating title and order is not allowed
        data = {
            'title': 'New workspace title',
            'ordering': {
                'obj_id': 'todolist-1',
                'delta': '1',
                'subset_ids': ['todolist-1', 'todolist-2']}}
        with browser.expect_http_error(401):
            browser.open(self.workspace, method='PATCH',
                         headers=self.api_headers, data=json.dumps(data))

        # Only updating the order is allowed
        data = {
            'ordering': {
                'obj_id': 'todolist-1',
                'delta': '1',
                'subset_ids': ['todolist-1', 'todolist-2']}}
        browser.open(self.workspace, method='PATCH',
                     headers=self.api_headers, data=json.dumps(data))

        self.assertEqual(204, browser.status_code)

    @browsing
    def test_workspace_guest_is_not_allowed_to_update_order(self, browser):
        self.login(self.workspace_guest, browser)

        data = {
            'ordering': {
                'obj_id': 'todolist-1',
                'delta': '1',
                'subset_ids': ['todolist-1', 'todolist-2']}}

        with browser.expect_http_error(401):
            browser.open(self.workspace, method='PATCH',
                         headers=self.api_headers, data=json.dumps(data))

    @browsing
    def test_move_todo_into_a_todolist(self, browser):
        self.login(self.workspace_member, browser)

        self.assertEqual(0, len(self.todolist_general.objectValues()))

        data = {'source': self.todo.absolute_url()}
        browser.open('{}/@move'.format(self.todolist_general.absolute_url()),
                     method='POST', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            ['Fix user login'],
            [obj.title for obj in self.todolist_general.objectValues()])

    @browsing
    def test_move_todo_from_one_todolist_to_another(self, browser):
        self.login(self.workspace_member, browser)

        data = {'source': self.assigned_todo.absolute_url()}
        browser.open('{}/@move'.format(self.todolist_general.absolute_url()),
                     method='POST', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            ['Go live'],
            [obj.title for obj in self.todolist_general.objectValues()])
