from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing.freezer import freeze
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestWorkspaceDocumentWorkflow(IntegrationTestCase):

    def finalize_workspace_document(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace_document.absolute_url(),
                'opengever_workspace_document--TRANSITION--finalize--active_final',
            ),
            method='POST', headers=self.api_headers,
        )

    def revise_workspace_document(self, browser):
        browser.open(
            '{}/@workflow/{}'.format(
                self.workspace_document.absolute_url(),
                'opengever_workspace_document--TRANSITION--reopen--final_active',
            ),
            method='POST', headers=self.api_headers,
        )

    @browsing
    def test_admin_can_finalize_workspace_document(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.finalize_workspace_document(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace_document--TRANSITION--finalize--active_final',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace_document--STATUS--final',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Final',
            }
        )

    @browsing
    def test_admin_can_revise_workspace_document(self, browser):
        self.login(self.workspace_admin, browser)
        with freeze(datetime(2020, 9, 4, 10, 30, tzinfo=pytz.UTC)):
            self.finalize_workspace_document(browser)
            self.revise_workspace_document(browser)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json,
            {
                u'action': u'opengever_workspace_document--TRANSITION--reopen--final_active',
                u'actor': u'fridolin.hugentobler',
                u'comments': u'',
                u'review_state': u'opengever_workspace_document--STATUS--active',
                u'time': u'2020-09-04T10:30:00+00:00',
                u'title': u'Active',
            }
        )

    @browsing
    def test_member_cannot_finalize_workspace_document(self, browser):
        self.login(self.workspace_member, browser)
        with browser.expect_http_error(400):
            self.finalize_workspace_document(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition 'opengever_workspace_docum"
                    "ent--TRANSITION--finalize--active_final'.\nValid transitions"
                    " are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    @browsing
    def test_member_cannot_revise_workspace_document(self, browser):
        self.login(self.workspace_admin, browser)
        self.finalize_workspace_document(browser)
        self.assertEqual(
            browser.json[u'review_state'],
            u'opengever_workspace_document--STATUS--final',
        )

        self.login(self.workspace_member, browser)
        with browser.expect_http_error(400):
            self.revise_workspace_document(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition 'opengever_workspace_docum"
                    "ent--TRANSITION--reopen--final_active'.\nValid transitions"
                    " are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    @browsing
    def test_cannot_finalize_if_checked_out_documents(self, browser):
        self.login(self.workspace_admin, browser)
        browser.open(
            '{}/@checkout'.format(self.workspace_document.absolute_url()),
            method='POST', headers=self.api_headers,
        )
        with browser.expect_http_error(400):
            self.finalize_workspace_document(browser)
        self.assertEqual(
            browser.json,
            {
                u'error': {
                    u'message': u"Invalid transition 'opengever_workspace_docum"
                    "ent--TRANSITION--finalize--active_final'.\nValid transitions"
                    " are:\n",
                    u'type': u'Bad Request',
                },
            },
        )

    @browsing
    def test_cannot_check_out_if_finalized_documents(self, browser):
        self.login(self.workspace_admin, browser)
        self.finalize_workspace_document(browser)
        self.assertEqual(
            browser.json[u'review_state'],
            u'opengever_workspace_document--STATUS--final',
        )

        with browser.expect_http_error(401):
            browser.open(
                '{}/@checkout'.format(self.workspace_document.absolute_url()),
                method='POST', headers=self.api_headers,)
        self.assertEqual(
            browser.json,
            {
                u'message': u"You are not authorized to access this resource.",
                u'type': u'Unauthorized',
            },
        )
