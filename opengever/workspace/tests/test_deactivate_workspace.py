from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing.freezer import freeze
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestDeactivateWorkspace(IntegrationTestCase):

    def deactivate_workspace(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace.absolute_url(),
                'opengever_workspace--TRANSITION--deactivate--active_inactive',
            ),
            method='POST', headers=self.api_headers,
        )

    def reactivate_workspace(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace.absolute_url(),
                'opengever_workspace--TRANSITION--reactivate--inactive_active',
            ),
            method='POST', headers=self.api_headers,
        )

    @browsing
    def test_admin_can_deactivate_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.deactivate_workspace(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace--TRANSITION--deactivate--active_inactive',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace--STATUS--inactive',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Inactive',
            }
        )

    @browsing
    def test_admin_can_reactivate_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.deactivate_workspace(browser)
            self.reactivate_workspace(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace--TRANSITION--reactivate--inactive_active',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace--STATUS--active',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Active',
            }
        )

    @browsing
    def test_member_cannot_deactivate_workspace(self, browser):
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(400):
            self.deactivate_workspace(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition 'opengever_workspace--TRA"
                    "NSITION--deactivate--active_inactive'.\nValid transitions"
                    " are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    @browsing
    def test_member_cannot_reactivate_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        self.assertEqual(
            browser.json[u'review_state'],
            u'opengever_workspace--STATUS--inactive',
        )

        self.login(self.workspace_member, browser)
        with browser.expect_http_error(400):
            self.reactivate_workspace(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition 'opengever_workspace--TRA"
                    "NSITION--reactivate--inactive_active'.\nValid transitions"
                    " are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    @browsing
    def test_cannot_deactivate_workspace_if_checked_out_documents(self, browser):
        self.login(self.workspace_admin, browser)
        browser.open(
            '{}/@checkout'.format(self.workspace_document.absolute_url()),
            method='POST', headers=self.api_headers,
        )
        with browser.expect_http_error(400):
            self.deactivate_workspace(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u'Workspace contains checked out documents.',
                    u'type': u'PreconditionsViolated',
                },
            },
        )

    @browsing
    def test_cannot_add_document_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'@type': 'opengever.document.document'}),
            )
        with browser.expect_http_error(401):
            browser.open(
                self.workspace_folder, method='POST', headers=self.api_headers,
                data=json.dumps({'@type': 'opengever.document.document'}),
            )

    @browsing
    def test_cannot_add_folder_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'@type': 'opengever.workspace.folder'}),
            )

    @browsing
    def test_cannot_add_todo_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'@type': 'opengever.workspace.todo'}),
            )

    @browsing
    def test_cannot_add_todolist_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace, method='POST', headers=self.api_headers,
                data=json.dumps({'@type': 'opengever.workspace.todolist'}),
            )

    @browsing
    def test_cannot_modify_document_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace_document, method='PATCH',
                headers=self.api_headers, data=json.dumps({'title': 'Foo'}),
            )

    @browsing
    def test_cannot_modify_folder_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.workspace_folder, method='PATCH',
                headers=self.api_headers, data=json.dumps({'title': 'Foo'}),
            )

    @browsing
    def test_cannot_modify_todo_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.todo, method='PATCH', headers=self.api_headers,
                data=json.dumps({'title': 'Foo'}),
            )

    @browsing
    def test_cannot_modify_todolist_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.todolist_general, method='PATCH',
                headers=self.api_headers, data=json.dumps({'title': 'Foo'}),
            )

    @browsing
    def test_cannot_delete_todo_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(self.todo, method='DELETE', headers=self.api_headers)

    @browsing
    def test_cannot_delete_todolist_in_deactivated_workspace(self, browser):
        self.login(self.workspace_admin, browser)
        self.deactivate_workspace(browser)
        with browser.expect_http_error(401):
            browser.open(
                self.todolist_general, method='DELETE',
                headers=self.api_headers,
            )
