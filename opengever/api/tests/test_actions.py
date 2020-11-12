from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.resolve import LockingResolveManager
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashable
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from plone.protect import createToken
import transaction


class FileActionsTestBase(IntegrationTestCase):

    features = ('bumblebee',)
    maxDiff = None

    def get_file_actions(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['file_actions']


class ObjectButtonsTestBase(IntegrationTestCase):

    maxDiff = None

    def get_object_buttons(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['object_buttons']


class TestFileActionsGetForNonDocumentishTypes(FileActionsTestBase):

    @browsing
    def test_available_file_actions_for_plone_site(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.portal))

    @browsing
    def test_available_file_actions_for_repository_root(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.repository_root))

    @browsing
    def test_available_file_actions_for_repository_folder(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.branch_repofolder))

    @browsing
    def test_available_file_actions_for_dossier(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.dossier))

    @browsing
    def test_available_file_actions_for_task(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.task))

    @browsing
    def test_available_file_actions_for_workspace_root(self, browser):
        self.login(self.workspace_member, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.workspace_root))

    @browsing
    def test_available_file_actions_for_workspace(self, browser):
        self.login(self.workspace_member, browser)
        expected_file_actions = []

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.workspace))


class TestFileActionsGetForMails(FileActionsTestBase):

    @browsing
    def test_available_file_actions(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.mail_eml))


class TestFileActionsGetForDocuments(FileActionsTestBase):

    @browsing
    def test_available_file_actions(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_oc_zem_checkout_available_if_oc_checkout_deactivated(self, browser):
        self.deactivate_feature('officeconnector-checkout')
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_zem_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_oc_unsupported_file_checkout_available_if_file_not_oc_editable(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.contentType = u'foo/bar'
        expected_file_actions = [
            {u'id': u'oc_unsupported_file_checkout',
             u'title': u'Checkout',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_checkin_available_if_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        expected_file_actions = [
            {u'id': u'oc_direct_edit',
             u'title': u'Edit',
             u'icon': u''},
            {u'id': u'checkin_without_comment',
             u'title': u'Checkin without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Checkin with comment',
             u'icon': u''},
            {u'id': u'cancel_checkout',
             u'title': u'Cancel checkout',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_checkin_available_if_checked_out_by_current_user_oc_checkout_deactivated(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        expected_file_actions = [
            {u'id': u'oc_direct_edit',
             u'title': u'Edit',
             u'icon': u''},
            {u'id': u'checkin_without_comment',
             u'title': u'Checkin without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Checkin with comment',
             u'icon': u''},
            {u'id': u'cancel_checkout',
             u'title': u'Cancel checkout',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]

        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_checkin_only_available_for_managers_if_checked_out_by_other_user(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        self.login(self.manager, browser)
        expected_manager_file_actions = [
            {u'id': u'checkin_without_comment',
             u'title': u'Checkin without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Checkin with comment',
             u'icon': u''},
            {u'id': u'cancel_checkout',
             u'title': u'Cancel checkout',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_manager_file_actions,
                         self.get_file_actions(browser, self.document))

        self.login(self.dossier_manager, browser)
        expected_dossier_manager_file_actions = [
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_dossier_manager_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_attach_not_available_if_feature_disabled(self, browser):
        self.deactivate_feature('officeconnector-attach')
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_oneoffixx_retry_available_for_shadow_documents(self, browser):
        self.activate_feature('oneoffixx')
        self.login(self.manager, browser)
        expected_file_actions = [
            {u'id': u'oneoffixx_retry',
             u'title': u'Oneoffixx retry',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.shadow_document))

    @browsing
    def test_open_as_pdf_not_available_if_bumblebee_disabled(self, browser):
        self.deactivate_feature('bumblebee')
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))


class TestTrashingActionsForDocuments(FileActionsTestBase):

    @browsing
    def test_trashing_available_for_document(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_untrashing_available_for_trashed_document(self, browser):
        self.login(self.regular_user, browser)

        trasher = ITrashable(self.document)
        trasher.trash()

        expected_file_actions = [
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'untrash_document',
             u'title': u'Untrash document',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))


class TestNewTaskFromDocumentAction(FileActionsTestBase):

    @browsing
    def test_task_from_doc_not_available_for_doc_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-resolve',
                     data={'_authenticator': createToken()})
        expected_file_actions = [
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.resolvable_document))

    @browsing
    def test_task_from_doc_not_available_for_doc_in_task(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.taskdocument))

    @browsing
    def test_task_from_doc_not_available_for_doc_in_inbox(self, browser):
        self.login(self.secretariat_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.inbox_document))

    @browsing
    def test_task_from_doc_not_available_for_doc_in_private_dossier(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_direct_checkout',
             u'title': u'Checkout and edit',
             u'icon': u''},
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            {u'id': u'trash_document',
             u'title': u'Trash document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.private_document))

    @browsing
    def test_task_from_doc_not_available_for_doc_in_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'download_copy',
             u'title': u'Download copy',
             u'icon': u''},
            {u'id': u'attach_to_email',
             u'title': u'Attach to email',
             u'icon': u''},
            {u'id': u'open_as_pdf',
             u'title': u'Open as PDF',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.inactive_document))


class TestFolderActions(IntegrationTestCase):

    features = ('bumblebee',)
    maxDiff = None
    createTaskAction = {
        u'id': u'create_task',
        u'title': u'Create Task',
        u'icon': u'',}

    def get_folder_buttons(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['folder_buttons']

    @browsing
    def test_create_task_available_in_open_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.assertIn(self.createTaskAction,
                      self.get_folder_buttons(browser, self.resolvable_dossier))

    @browsing
    def test_create_task_available_in_task(self, browser):
        self.login(self.regular_user, browser)
        self.assertIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.task))

    @browsing
    def test_create_task_available_in_meetingdossier(self, browser):
        self.login(self.regular_user, browser)
        self.assertIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.meeting_dossier))

    @browsing
    def test_create_task_not_available_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-resolve',
                     data={'_authenticator': createToken()})
        self.assertNotIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.resolvable_dossier))

    @browsing
    def test_create_task_not_available_in_inbox(self, browser):
        self.login(self.secretariat_user, browser)
        self.assertNotIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.inbox))

    @browsing
    def test_create_task_not_available_in_private_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assertNotIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.private_dossier))

    @browsing
    def test_create_task_not_available_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assertNotIn(self.createTaskAction,
                         self.get_folder_buttons(browser, self.inactive_dossier))


class TestWorkspaceClientFolderActions(FunctionalWorkspaceClientTestCase):

    list_workspaces_action = {
        u'id': u'list_workspaces',
        u'title': u'List workspaces',
        u'icon': u''}

    copy_documents_to_workspace_action = {
        u'id': u'copy_documents_to_workspace',
        u'title': u'Copy documents to workspace',
        u'icon': u''}

    copy_documents_from_workspace_action = {
        u'id': u'copy_documents_from_workspace',
        u'title': u'Copy documents from workspace',
        u'icon': u''}

    workspace_actions = [list_workspaces_action,
                         copy_documents_to_workspace_action,
                         copy_documents_from_workspace_action]

    def get_actions(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        return browser.json['folder_buttons'] + browser.json['folder_actions']

    def link_workspace(self, obj):
        manager = ILinkedWorkspaces(obj)
        manager.storage.add(self.workspace.UID())
        transaction.commit()

    def assert_workspace_actions(self, browser, context, expected):
        all_actions = self.get_actions(browser, context)
        workspace_action_ids = {each['id'] for each in self.workspace_actions}
        available = [
            action for action in all_actions
            if action['id'] in workspace_action_ids
        ]

        self.assertEqual(sorted(available), sorted(expected))

    def assert_workspace_actions_available(self, browser, context):
        self.assert_workspace_actions(browser, context, self.workspace_actions)

    def assert_workspace_actions_not_available(self, browser, context):
        self.assert_workspace_actions(browser, context, [])

    @browsing
    def test_copy_documents_actions_available_in_dossier_with_linked_workspaces(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            actions = self.get_actions(browser, self.dossier)
            self.assertIn(self.copy_documents_to_workspace_action,
                          actions)
            self.assertIn(self.copy_documents_from_workspace_action,
                          actions)

    @browsing
    def test_workspace_actions_not_available_in_subdossier(self, browser):
        browser.login()
        subdossier = create(Builder('dossier').within(self.dossier))
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            self.assert_workspace_actions_not_available(browser, subdossier)

    @browsing
    def test_copy_documents_actions_not_available_in_dossier_without_linked_workspaces(self, browser):
        browser.login()
        with self.workspace_client_env():
            actions = self.get_actions(browser, self.dossier)
            self.assertNotIn(self.copy_documents_to_workspace_action,
                             actions)
            self.assertNotIn(self.copy_documents_from_workspace_action,
                             actions)

    @browsing
    def test_workspace_actions_not_available_in_repository(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            self.assert_workspace_actions_not_available(browser, self.leaf_repofolder)

    @browsing
    def test_workspaces_actions_only_available_if_feature_activated(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)

            self.assert_workspace_actions_available(browser, self.dossier)

            self.enable_feature(False)
            transaction.commit()

            self.assert_workspace_actions_not_available(browser, self.dossier)

    @browsing
    def test_workspaces_actions_only_available_if_user_has_permission_to_use_workspace_client(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)

            self.assert_workspace_actions_available(browser, self.dossier)

            roles = api.user.get_roles()
            roles.remove('WorkspaceClientUser')
            self.grant(*roles)

            self.assert_workspace_actions_not_available(browser, self.dossier)

    @browsing
    def test_workspaces_actions_not_available_if_user_has_no_permission(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)

            self.assert_workspace_actions_available(browser, self.dossier)

            # global permissions are setup in a weird way
            self.grant('WorkspaceClientUser', 'Member')
            self.dossier.__ac_local_roles_block__ = True
            self.grant('Reader', on=self.dossier)

            self.assert_workspace_actions(browser, self.dossier,
                                          [self.list_workspaces_action])

    @browsing
    def test_workspaces_actions_not_available_if_dossier_is_not_open(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)

            #self.assert_workspace_actions_available(browser, self.dossier)

            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-deactivate')
            transaction.commit()

            self.assert_workspace_actions(browser, self.dossier,
                                          [self.list_workspaces_action])


class TestObjectButtonsGetForDocuments(ObjectButtonsTestBase):

    @browsing
    def test_document_does_not_have_delete_object_button(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy Item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move Item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.document),
        )

    @browsing
    def test_document_in_inbox_has_create_forwarding_button(self, browser):
        self.login(self.secretariat_user, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'create_forwarding', u'title': u'Forward'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy Item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move Item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.inbox_document),
        )

    @browsing
    def test_actions_for_document_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()

        self.login(self.regular_user, browser)

        expected_object_buttons = [
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy Item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.resolvable_document),
        )

    @browsing
    def test_actions_for_document_in_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)

        expected_object_buttons = [
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy Item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.inactive_document),
        )


class TestObjectButtonsGetForTemplates(ObjectButtonsTestBase):

    @browsing
    def test_template_has_delete_object_button(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy Item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move Item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.normal_template),
        )


class TestWebActionsIntegration(IntegrationTestCase):

    @browsing
    def test_integrate_webactions_in_its_own_action_category(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@actions',
                     method='GET', headers=self.api_headers)
        self.assertNotIn('webactions', browser.json)

        self.login(self.webaction_manager, browser=browser)
        create(Builder('webaction').having(enabled=True))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@actions',
                     method='GET', headers=self.api_headers)
        self.assertIn('webactions', browser.json)

    @browsing
    def test_integrate_webactions_on_expand(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='?expand=actions',
                     method='GET', headers=self.api_headers)
        actions = browser.json.get('@components').get('actions')
        self.assertNotIn('webactions', actions)

        self.login(self.webaction_manager, browser=browser)
        create(Builder('webaction').having(enabled=True))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='?expand=actions',
                     method='GET', headers=self.api_headers)
        actions = browser.json.get('@components').get('actions')
        self.assertIn('webactions', actions)

    @browsing
    def test_list_available_webactions(self, browser):
        self.login(self.webaction_manager, browser=browser)
        create(Builder('webaction')
               .having(
                   title=u'Open in ExternalApp',
                   enabled=True,
            ))
        create(Builder('webaction')
               .having(
                   title=u'Open in InternalApp',
                   enabled=True,
        ))
        create(Builder('webaction')
               .having(
                   title=u'Open in BrokenApp',
                   enabled=False,
            ))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@actions',
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            [u'Open in ExternalApp', u'Open in InternalApp'],
            [action.get('title') for action in browser.json.get('webactions')])

    @browsing
    def test_webaction_serialization_in_actions_endpoint(self, browser):
        self.login(self.webaction_manager, browser=browser)
        create(Builder('webaction').having(
            target_url='http://localhost/foo?location={path}'))

        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='/@actions',
                     method='GET', headers=self.api_headers)

        self.assertEqual([
            {
                u'action_id': 0,
                u'display': u'actions-menu',
                u'mode': u'self',
                u'icon_data': None,
                u'icon_name': None,
                u'target_url': u'http://localhost/foo?location=%2Fplone%2Fordnungssystem%2Ffuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1&context=http%3A%2F%2Fnohost%2Fplone%2Fordnungssystem%2Ffuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1&orgunit=fa',
                u'title': u'Open in ExternalApp'
            }],
            browser.json.get('webactions'))
