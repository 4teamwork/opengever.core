from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashable
from plone.protect import createToken


class FileActionsTestBase(IntegrationTestCase):

    features = ('bumblebee',)
    maxDiff = None

    def get_file_actions(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['file_actions']


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
