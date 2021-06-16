from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestDeleteWorkspaceDocument(IntegrationTestCase):

    @browsing
    def test_members_can_permanently_delete_document(self, browser):
        self.login(self.workspace_member, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_admins_can_permanently_delete_document(self, browser):
        self.login(self.workspace_admin, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_managers_can_permanently_delete_document(self, browser):
        self.login(self.manager, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_guests_cannot_permanently_delete_document(self, browser):
        self.login(self.workspace_guest, browser)
        with browser.expect_http_error(401):
            browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
