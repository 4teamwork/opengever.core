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
from zExceptions import BadRequest
from zope.schema import getSchemaValidationErrors
import json


class TestToDo(SolrIntegrationTestCase):

    def create_to_do(self, browser, workspace, title, responsible=None):
        browser.visit(workspace)
        factoriesmenu.add('To-do item')

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

    def test_is_completed_indexer(self):
        self.login(self.workspace_member)

        self.assertFalse(solr_data_for(self.todo, 'is_completed'))

        api.content.transition(
            obj=self.todo,
            transition='opengever_workspace_todo--TRANSITION--complete--active_completed')

        self.todo.reindexObject()
        self.commit_solr()

        self.assertTrue(solr_data_for(self.todo, 'is_completed'))

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
    def test_create_with_all(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, method='POST', headers=self.api_headers,
            data=json.dumps({
                'title': 'Ein komplett ausgefuelltes ToDo',
                '@type': 'opengever.workspace.todo',
                'text': 'Eine ToDo-Beschreibung',
                'is_completed': False,
                'responsible': self.workspace_member.id,
                'deadline': '2024-02-13',
                'external_reference': 'www.4teamwork.ch',
            }))

        self.assertEqual(201, browser.status_code)
        self.assertDictContainsSubset({
            'title': 'Ein komplett ausgefuelltes ToDo',
            '@type': 'opengever.workspace.todo',
            'text': 'Eine ToDo-Beschreibung',
            'is_completed': False,
            'responsible': {
                u'token': self.workspace_member.id, 
                u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
            },
            'deadline': '2024-02-13',
            'external_reference': 'www.4teamwork.ch',
        }, browser.json)

    @browsing
    def test_create_with_todo_feature_disabled(self, browser):
        self.deactivate_feature('workspace-todo')
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'title': 'Ein ToDo',
                                 '@type': 'opengever.workspace.todo'}))

        self.assertEqual('Disallowed subobject type: opengever.workspace.todo',
                         browser.json['error']['message'])

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
    def test_document_related_with_todo(self, browser):
        self.login(self.workspace_member, browser)
        self.set_related_items(self.todo, [self.workspace_document])
        browser.open(self.todo, method='GET', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(browser.json['relatedItems']))

        self.assertEqual(
            {u'@id': self.workspace_document.absolute_url(),
             u'@type': self.workspace_document.portal_type,
             u'UID': u'createworkspace00000000000000003',
             u'checked_out': None,
             u'description': u'',
             u'file_extension': u'.txt',
             u'is_leafnode': None,
             u'review_state': u'opengever_workspace_document--STATUS--active',
             u'title': self.workspace_document.title},
            browser.json['relatedItems'][0])

    @browsing
    def test_document_outside_workspace_cannot_be_set_in_related_items_field(self, browser):
        self.login(self.workspace_member, browser)
        data = {'relatedItems': [{'@id': self.workspace_document.absolute_url()}]}
        browser.open(self.todo, method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))
        self.assertEqual(204, browser.status_code)

        data = {'relatedItems': [{'@id': self.document.absolute_url()}]}
        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.todo, method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.assertEqual("[{'field': 'relatedItems', 'message': u'Constraint not satisfied',"
                         " 'error': 'ValidationError'}]", str(cm.exception))

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
        self.assertEqual(1, len(responses))

        browser.open(self.todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new login'}))

        responses = IResponseContainer(self.todo).list()
        self.assertEqual(2, len(responses))

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
    def test_members_can_delete_todos(self, browser):
        self.login(self.workspace_member, browser)
        todo_id = self.todo.id
        browser.open(self.todo, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(todo_id, self.workspace.objectIds())

    @browsing
    def test_admins_can_delete_todos(self, browser):
        self.login(self.workspace_admin, browser)
        todo_id = self.todo.id
        browser.open(self.todo, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(todo_id, self.workspace.objectIds())

    @browsing
    def test_managers_can_delete_todos(self, browser):
        self.login(self.manager, browser)
        todo_id = self.todo.id
        browser.open(self.todo, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(todo_id, self.workspace.objectIds())

    @browsing
    def test_guests_cannot_delete_todos(self, browser):
        self.login(self.workspace_guest, browser)
        with browser.expect_http_error(403):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

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

    @browsing
    def test_complete_todo(self, browser):
        self.login(self.workspace_member, browser)
        self.assertFalse(self.todo.is_completed)

        browser.open(
            self.todo, method='POST', headers=self.api_headers,
            view="@workflow/opengever_workspace_todo--TRANSITION--complete--active_completed")

        self.assertEqual(200, browser.status_code)
        self.assertTrue(self.todo.is_completed)

    @browsing
    def test_open_todo(self, browser):
        self.login(self.workspace_member, browser)
        self.assertTrue(self.completed_todo.is_completed)

        browser.open(
            self.completed_todo, method='POST', headers=self.api_headers,
            view="@workflow/opengever_workspace_todo--TRANSITION--open--completed_active")

        self.assertEqual(200, browser.status_code)
        self.assertFalse(self.completed_todo.is_completed)

    @browsing
    def test_contains_is_completed(self, browser):
        self.login(self.workspace_member, browser)

        browser.open(self.todo, method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['is_completed'])

        browser.open(self.completed_todo, method="GET", headers=self.api_headers)
        self.assertTrue(browser.json['is_completed'])
