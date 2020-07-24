from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashable
import json


class TestWorkflowPost(IntegrationTestCase):

    @browsing
    def test_transition_reassigning_task_and_revoking_users_permissions_can_be_executed(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            'responsible': {
                'token': 'rk:{}'.format(self.dossier_responsible.getId())
            }
        }
        # this reassigns the task so that `regular_user` no longer has access
        browser.open(
            self.task_in_protected_dossier.absolute_url() + '/@workflow/task-transition-reassign',
            json.dumps(data), method='POST', headers=self.api_headers
        )

        self.assertDictContainsSubset(
            {u'title': u'task-state-in-progress',
             u'actor': u'kathi.barfuss',
             u'action': u'task-transition-reassign',
             u'review_state': u'task-state-in-progress'},
            browser.json
        )

    @browsing
    def test_transition_close_task_and_revoking_users_permissions_can_be_executed(self, browser):
        self.login(self.regular_user, browser=browser)

        # only direct execution tasks can be closed directly
        self.task_in_protected_dossier.task_type = 'direct-execution'

        # this closes the task so that `regular_user` no longer has access
        browser.open(
            self.task_in_protected_dossier.absolute_url() + '/@workflow/task-transition-in-progress-tested-and-closed',
            method='POST', headers=self.api_headers
        )

        self.assertDictContainsSubset(
            {u'title': u'task-state-tested-and-closed',
             u'actor': u'kathi.barfuss',
             u'action': u'task-transition-in-progress-tested-and-closed',
             u'review_state': u'task-state-tested-and-closed'},
            browser.json
        )

    @browsing
    def test_transition_remove_document_and_revoking_users_permission_can_be_executed(self, browser):
        self.login(self.manager)
        # allow `regular_user` to remove gever content
        self.portal.manage_permission(
            'Remove GEVER content', roles=['Editor'], acquire=True)

        self.login(self.regular_user, browser=browser)
        ITrashable(self.document).trash()
        # this soft-deletes the document so that `regular_user` no longer has
        # access
        browser.open(
            self.document.absolute_url() + '/@workflow/document-transition-remove',
            method='POST', headers=self.api_headers)

        self.assertDictContainsSubset(
            {u'title': u'document-state-removed',
             u'actor': u'kathi.barfuss',
             u'action': u'document-transition-remove',
             u'review_state': u'document-state-removed'},
            browser.json
        )

    @browsing
    def test_calling_endpoint_without_transition_gives_400(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(
                self.dossier.absolute_url() + '/@workflow',
                method='POST', headers=self.api_headers)

        self.assertEqual('Bad Request', browser.json['error']['type'])
        self.assertIn(u"Invalid transition 'None'",
                      browser.json['error']['message'])

    @browsing
    def test_calling_workflow_with_additional_path_segments_results_in_404(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=404):
            browser.open(
                self.dossier.absolute_url() + '/@workflow/dossier-transition-resolve/invalid',
                method='POST', headers=self.api_headers)

        self.assertEqual('NotFound', browser.json['type'])

    @browsing
    def test_invalid_transition_results_in_400(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(
                self.dossier.absolute_url() + '/@workflow/invalid-transition',
                method='POST', headers=self.api_headers)

        self.assertEqual('Bad Request', browser.json['error']['type'])
        self.assertIn(u"Invalid transition 'invalid-transition'",
                      browser.json['error']['message'])
