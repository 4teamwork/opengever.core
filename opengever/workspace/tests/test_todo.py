from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.response import IResponseContainer
from opengever.base.response import IResponseSupported
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from opengever.workspace.todo import IToDoSchema
from plone import api
from unittest import skip
from zope.schema import getSchemaValidationErrors
import json
import opengever.workspace.subscribers


class TestToDo(SolrIntegrationTestCase):

    def create_to_do(self, browser, workspace, title, responsible=None):
        browser.visit(workspace)
        factoriesmenu.add('ToDo')

        with self.observe_children(self.workspace) as children:
            form = browser.find_form_by_field('Title')
            form.fill({'Title': title})
            if responsible:
                form.find_widget('Responsible').fill(responsible,
                                                     auto_org_unit=False)
            form.save()

        if not len(children.get("added")) == 1:
            return None

        return children.get("added").pop()

    @browsing
    def test_todo_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        todo = self.create_to_do(browser, self.workspace, u'Ein ToDo')

        assert_no_error_messages(browser)
        self.assertIsNotNone(todo)

    @skip("With the current state of the source vocabularies we cannot handle "
          "both the fact that users that lost their permissions remain valid "
          "and that we cannot set those users as responsibles. They are "
          "nevertheless excluded from the search, and therefore not proposed "
          "to the user")
    @browsing
    def test_only_actual_workspace_users_can_be_set_as_responsibles(self, browser):
        self.login(self.workspace_member, browser)
        todo = self.create_to_do(browser, self.workspace, u'Ein ToDo',
                                 self.regular_user.id)

        # invalid userids are silently replaced by the default value in
        # the keyword widget, see z3c.form.widget.SequenceWidget.extract
        assert_no_error_messages(browser)
        self.assertIsNotNone(todo)
        self.assertIsNone(todo.responsible)

        RoleAssignmentManager(self.workspace).add_or_update(
            self.regular_user.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)
        self.workspace.reindexObjectSecurity()

        todo = self.create_to_do(browser, self.workspace, u'Ein ToDo',
                                 self.regular_user.id)
        assert_no_error_messages(browser)
        self.assertIsNotNone(todo)
        self.assertIsNotNone(todo.responsible)
        self.assertEqual(self.regular_user.id, todo.responsible)

    @browsing
    def test_reponsible_remains_valid_after_local_roles_removed(self, browser):
        self.login(self.workspace_member, browser)

        RoleAssignmentManager(self.workspace).add_or_update(
            self.regular_user.id, ['WorkspaceGuest'], ASSIGNMENT_VIA_INVITATION)
        self.workspace.reindexObjectSecurity()

        todo = self.create_to_do(browser, self.workspace, u'Ein ToDo',
                                 self.regular_user.id)

        self.assertIsNotNone(todo)
        self.assertEqual(self.regular_user.id, todo.responsible)
        self.assertEqual([], getSchemaValidationErrors(IToDoSchema, todo))

        RoleAssignmentManager(self.workspace).clear_by_cause_and_principal(
            ASSIGNMENT_VIA_INVITATION, self.regular_user.id)
        self.workspace.reindexObjectSecurity()

        getSchemaValidationErrors(IToDoSchema, todo)
        self.assertEqual([], getSchemaValidationErrors(IToDoSchema, todo))

    def test_searchable_text(self):
        self.login(self.workspace_member)

        indexed_searchable_text = solr_data_for(self.todo, 'SearchableText')
        self.assertIn(self.todo.title, indexed_searchable_text)
        self.assertIn(self.todo.text, indexed_searchable_text)

    @browsing
    def test_todo_number_hard_limit(self, browser):
        self.login(self.workspace_member, browser)

        catalog = api.portal.get_tool("portal_catalog")
        todos = catalog.unrestrictedSearchResults(
                    path=self.workspace.absolute_url_path(),
                    portal_type='opengever.workspace.todo')
        opengever.workspace.subscribers.TODO_NUMBER_LIMIT = len(todos) + 1

        browser.visit(self.workspace)
        factoriesmenu.add('ToDo')
        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Ein ToDo'})
        form.save()

        assert_no_error_messages(browser)

        browser.visit(self.workspace)
        factoriesmenu.add('ToDo')
        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Ein anderes ToDo'})
        with browser.expect_http_error(500):
            form.save()

    def test_todo_supports_responses(self):
        self.login(self.workspace_member)

        IResponseSupported.providedBy(self.todo)


class TestAPISupportForTodo(IntegrationTestCase):

    @browsing
    def test_create(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({'title': 'Ein ToDo',
                             '@type': 'opengever.workspace.todo'}))

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Ein ToDo',
                         browser.json['title'])
        self.assertEqual('todo-4', browser.json['id'])

    @browsing
    def test_read(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.todo, method='GET', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual(u'Fix user login', browser.json['title'])
        self.assertEqual(u'opengever.workspace.todo', browser.json['@type'])
        self.assertEqual(u'opengever_workspace_todo--STATUS--active',
                         browser.json['review_state'])

    @browsing
    def test_update(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new login'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xc4 new login', self.todo.title)

    @browsing
    def test_update_adds_response_object_with_changes(self, browser):
        self.login(self.workspace_member, browser)

        responses = IResponseContainer(self.todo).list()
        self.assertEqual(0, len(responses))

        browser.open(self.todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new login'}))

        responses = IResponseContainer(self.todo).list()
        self.assertEqual(1, len(responses))

        last_response = responses[-1]
        self.assertEqual('', last_response.text)
        self.assertEqual('schema_field', last_response.response_type)
        self.assertItemsEqual(
            [
                {
                    'field_id': 'title',
                    'before': u'Fix user login',
                    'after': u'\xc4 new login',
                    'field_title': ''
                }
            ],
            last_response.changes)

    @browsing
    def test_deletion_is_only_possible_for_managers(self, browser):
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.workspace_admin, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.workspace_owner, browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

        self.login(self.manager, browser)
        todo_id = self.todo.id
        browser.open(self.todo, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(todo_id, self.workspace.objectIds())

    @browsing
    def test_move_todo_adds_response_object_with_changes(self, browser):
        self.login(self.workspace_member, browser)

        def move_todo(todo, target):
            todo_id = todo.getId()
            data = {'source': todo.absolute_url()}
            browser.open('{}/@move'.format(target.absolute_url()),
                         method='POST', headers=self.api_headers,
                         data=json.dumps(data))

            return IResponseContainer(todo).list()[-1], target[todo_id]

        response, todo = move_todo(self.todo, self.todolist_general)
        self.assertEqual('move', response.response_type)
        self.assertItemsEqual(
            [
                {
                    'field_id': '',
                    'before': u'',
                    'after': u'Allgemeine Informationen',
                    'field_title': ''
                }
            ],
            response.changes)

        response, todo = move_todo(todo, self.todolist_introduction)
        self.assertItemsEqual(
            [
                {
                    'field_id': '',
                    'before': u'Allgemeine Informationen',
                    'after': u'Projekteinf\xfchrung',
                    'field_title': ''
                }
            ],
            response.changes)

        response, todo = move_todo(todo, self.workspace)
        self.assertItemsEqual(
            [
                {
                    'field_id': '',
                    'before': u'Projekteinf\xfchrung',
                    'after': u'',
                    'field_title': ''
                }
            ],
            response.changes)
