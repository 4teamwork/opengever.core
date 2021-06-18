from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher


class APITestDeleteMixin(object):

    def assert_cannot_delete(self, obj, browser, code=401):
        parent = aq_parent(aq_inner(obj))
        with self.observe_children(parent) as children, browser.expect_http_error(code):
            browser.open(obj, method='DELETE', headers=self.api_headers)
        self.assertEqual(set(), children['removed'])

    def assert_can_delete(self, obj, browser):
        parent = aq_parent(aq_inner(obj))
        with self.observe_children(parent) as children:
            browser.open(obj, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertEqual({obj}, children['removed'])


class DeleteGeverObjects(IntegrationTestCase, APITestDeleteMixin):

    @browsing
    def test_deleting_businesscasedossier_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.empty_dossier

        self.assert_cannot_delete(obj, browser, code=403)

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

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_task_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.task

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_proposal_requires_delete_objects_permission(self, browser):
        self.login(self.administrator, browser)
        obj = self.proposal

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("Delete objects", roles=["Administrator"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_disposition_requires_delete_objects_permission(self, browser):
        self.login(self.records_manager, browser)
        obj = self.disposition

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("Delete objects", roles=["Records Manager"])
        self.assert_can_delete(obj, browser)


class TestDeleteTeamraumObjects(IntegrationTestCase, APITestDeleteMixin):

    @browsing
    def test_deleting_todos_requires_delete_todos_permission(self, browser):
        self.login(self.workspace_guest, browser)
        obj = self.todo

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("opengever.workspace: Delete Todos", roles=["WorkspacesUser"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_todolist_requires_delete_todos_permission(self, browser):
        self.login(self.workspace_guest, browser)
        obj = self.todolist_general

        self.assert_cannot_delete(obj, browser, code=403)

        obj.manage_permission("opengever.workspace: Delete Todos", roles=["WorkspacesUser"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_workspace_meeting_agendaitem_requires_delete_agendaitems_permission(self, browser):
        self.login(self.workspace_guest, browser)
        obj = self.workspace_meeting_agenda_item

        self.assert_cannot_delete(obj, browser, code=403)

        self.workspace_meeting.manage_permission(
            "opengever.workspace: Delete Workspace Meeting Agenda Items",
            roles=["WorkspacesUser"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_workspace_folder_requires_delete_workspace_folders_permission(self, browser):
        self.login(self.workspace_member, browser)
        obj = self.workspace_folder
        ITrasher(obj).trash()

        self.workspace.manage_permission(
            "opengever.workspace: Delete Workspace Folders",
            roles=[])

        self.assert_cannot_delete(obj, browser, code=403)

        self.workspace.manage_permission(
            "opengever.workspace: Delete Workspace Folders",
            roles=["WorkspacesUser"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_deleting_workspace_folder_checks_permissions_recursively(self, browser):
        self.login(self.workspace_member, browser)
        subfolder = create(Builder("workspace folder").within(self.workspace_folder))
        ITrasher(self.workspace_folder).trash()

        subfolder.__ac_local_roles_block__ = True

        self.assert_cannot_delete(self.workspace_folder, browser, code=403)

        subfolder.__ac_local_roles_block__ = False
        self.assert_can_delete(self.workspace_folder, browser)

    @browsing
    def test_deleting_workspace_document_requires_delete_document_permission(self, browser):
        self.login(self.workspace_member, browser)
        obj = self.workspace_document
        ITrasher(obj).trash()

        self.workspace.manage_permission(
            "opengever.workspace: Delete Documents",
            roles=[])

        self.assert_cannot_delete(obj, browser, code=403)

        self.workspace.manage_permission(
            "opengever.workspace: Delete Documents",
            roles=["WorkspacesUser"])
        self.assert_can_delete(obj, browser)

    @browsing
    def test_members_can_permanently_delete_document(self, browser):
        self.login(self.workspace_member, browser)
        ITrasher(self.workspace_document).trash()
        self.assert_can_delete(self.workspace_document, browser)

    @browsing
    def test_members_can_permanently_delete_mail(self, browser):
        self.login(self.workspace_member, browser)
        ITrasher(self.workspace_mail).trash()
        self.assert_can_delete(self.workspace_mail, browser)

    @browsing
    def test_admins_can_permanently_delete_document(self, browser):
        self.login(self.workspace_admin, browser)
        ITrasher(self.workspace_document).trash()
        self.assert_can_delete(self.workspace_document, browser)

    @browsing
    def test_managers_can_permanently_delete_document(self, browser):
        self.login(self.manager, browser)
        ITrasher(self.workspace_document).trash()
        self.assert_can_delete(self.workspace_document, browser)

    @browsing
    def test_guests_cannot_permanently_delete_document(self, browser):
        with self.login(self.manager):
            ITrasher(self.workspace_document).trash()
        self.login(self.workspace_guest, browser)
        self.assert_cannot_delete(self.workspace_document, browser, code=403)
