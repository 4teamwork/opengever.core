from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class DeleteGeverObjects(IntegrationTestCase):

    def assert_cannot_delete(self, obj, browser, code=401):
        parent = aq_parent(aq_inner(obj))
        with self.observe_children(parent) as children, browser.expect_http_error(code):
            browser.open(obj, method='DELETE', headers=self.api_headers)
        self.assertEqual(set(), children['removed'])

    def assert_can_delete(self, obj, browser):
        parent = aq_parent(aq_inner(obj))
        with self.observe_children(parent) as children:
            browser.open(obj, method='DELETE', headers=self.api_headers)
        self.assertEqual({obj}, children['removed'])

    @browsing
    def test_deleting_businesscasedossier_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.empty_dossier

        self.assert_cannot_delete(obj, browser)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_document_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.subdocument

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_mail_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.mail_eml

        self.assert_cannot_delete(obj, browser)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_task_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.task

        self.assert_cannot_delete(obj, browser)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_proposal_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.proposal

        self.assert_cannot_delete(obj, browser)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_disposition_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.disposition

        # Admins have the Delete objects permission on dispositions...
        obj.manage_permission("Delete objects", roles=[])
        self.assert_cannot_delete(obj, browser)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)


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
