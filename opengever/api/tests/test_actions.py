from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.resolve import LockingResolveManager
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from plone.locking.interfaces import ILockable
from plone.namedfile.file import NamedBlobFile
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


class UIContextActionsTestBase(IntegrationTestCase):

    maxDiff = None

    def get_ui_context_actions(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['ui_context_actions']


class FolderActionsTestBase(IntegrationTestCase):

    maxDiff = None

    def get_folder_buttons(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['folder_buttons']


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


class TestFileActionsGetForNonDocumentishTypesForWorkspace(FileActionsTestBase):

    features = ('workspace', )

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

    @browsing
    def test_available_file_actions_for_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)
        expected_file_actions = [
            {u'icon': u'', u'id': u'trash_context', u'title': u'Trash'}
        ]
        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, self.workspace_folder),
        )

    @browsing
    def test_available_file_actions_for_trashed_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)
        ITrasher(self.workspace_folder).trash()
        expected_file_actions = [
            {u'icon': u'', u'id': u'untrash_context', u'title': u'Untrash'},
            {u'icon': u'', u'id': u'delete_workspace_context', u'title': u'Delete'}
        ]
        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, self.workspace_folder),
        )


class TestFileActionsGetForWorkspaceDocument(FileActionsTestBase):

    features = ('workspace', 'bumblebee')

    @browsing
    def test_available_file_actions_for_workspace_document(self, browser):
        self.login(self.workspace_member, browser)
        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'oc_direct_checkout', u'title': u'Checkout and edit'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'attach_to_email', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'},
            {u'icon': u'', u'id': u'trash_context', u'title': u'Trash'}
        ]
        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, self.workspace_document),
        )

    @browsing
    def test_available_file_actions_for_trashed_workspace_document(self, browser):
        self.login(self.workspace_member, browser)
        ITrasher(self.workspace_document).trash()
        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'attach_to_email', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'},
            {u'icon': u'', u'id': u'untrash_context', u'title': u'Untrash'},
            {u'icon': u'', u'id': u'delete_workspace_context', u'title': u'Delete'}
        ]
        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, self.workspace_document),
        )


class TestFileActionsGetForMails(FileActionsTestBase):

    @browsing
    def test_available_file_actions(self, browser):
        self.login(self.regular_user, browser)
        expected_file_actions = [
            {u'id': u'oc_view',
             u'title': u'View',
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
            {u'id': u'trash_context',
             u'title': u'Trash',
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
            {u'id': u'oc_view',
             u'icon': u'',
             u'title': u'View'},
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
            {u'id': u'trash_context',
             u'title': u'Trash',
             u'icon': u''},
            {u'id': u'new_task_from_document',
             u'title': u'New task from document',
             u'icon': u''},
            ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.document))

    @browsing
    def test_available_file_actions_if_document_checked_out_by_myself(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        expected_file_actions = [
            {u'id': u'oc_direct_edit',
             u'title': u'Edit',
             u'icon': u''},
            {u'id': u'checkin_without_comment',
             u'title': u'Check in without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Check in with comment',
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
    def test_available_file_actions_if_document_checked_out_by_another_user_without_a_version(self, browser):
        self.login(self.dossier_manager, browser)
        self.checkout_document(self.document)

        self.login(self.regular_user, browser)

        expected_file_actions = [
            {u'id': u'oc_view',
             u'title': u'View',
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
    def test_available_file_actions_if_document_checked_out_by_another_user_with_an_init_version(self, browser):
        self.login(self.dossier_manager, browser)
        self.checkout_document(self.document)

        # The file setter of a document will automatically create an init version
        self.document.file = NamedBlobFile(
            data='TEST DATA', filename=self.document.file.filename)

        self.login(self.regular_user, browser)

        expected_file_actions = [
            {u'id': u'oc_view',
             u'icon': u'',
             u'title': u'View'},
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
    def test_available_file_actions_if_document_checked_out_by_another_user_with_a_version(self, browser):
        self.login(self.dossier_manager, browser)
        self.checkout_document(self.document)
        self.document.update_file('first version', create_version=True)

        self.login(self.regular_user, browser)

        expected_file_actions = [
            {u'id': u'oc_view',
             u'icon': u'',
             u'title': u'View'},
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
    def test_oc_zem_checkout_available_if_oc_checkout_deactivated(self, browser):
        self.deactivate_feature('officeconnector-checkout')
        self.login(self.regular_user, browser)
        self.assertIn(
            {
                u'id': u'oc_zem_checkout',
                u'title': u'Checkout and edit',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_oc_unsupported_file_checkout_available_if_file_not_oc_editable(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.contentType = u'foo/bar'
        self.assertIn(
            {
                u'id': u'oc_unsupported_file_checkout',
                u'title': u'Checkout',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_checkin_available_if_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)

        expected_file_actions = [
            {u'id': u'oc_direct_edit',
             u'title': u'Edit',
             u'icon': u''},
            {u'id': u'checkin_without_comment',
             u'title': u'Check in without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Check in with comment',
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
             u'title': u'Check in without comment',
             u'icon': u''},
            {u'id': u'checkin_with_comment',
             u'title': u'Check in with comment',
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
        self.assertIn(
            {
                u'id': u'checkin_without_comment',
                u'title': u'Check in without comment',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )
        self.assertIn(
            {
                u'id': u'checkin_with_comment',
                u'title': u'Check in with comment',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )
        self.assertIn(
            {
                u'id': u'cancel_checkout',
                u'title': u'Cancel checkout',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

        self.login(self.dossier_manager, browser)
        self.assertNotIn(
            {
                u'id': u'checkin_without_comment',
                u'title': u'Check in without comment',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )
        self.assertNotIn(
            {
                u'id': u'checkin_with_comment',
                u'title': u'Check in with comment',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )
        self.assertNotIn(
            {
                u'id': u'cancel_checkout',
                u'title': u'Cancel checkout',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_attach_not_available_if_feature_disabled(self, browser):
        self.deactivate_feature('officeconnector-attach')
        self.login(self.regular_user, browser)
        self.assertNotIn(
            {u'icon': u'', u'id': u'attach_to_email', u'title': u'Attach to email'},
            self.get_file_actions(browser, self.document)
        )

    @browsing
    def test_oneoffixx_retry_available_for_shadow_documents(self, browser):
        self.activate_feature('oneoffixx')
        self.login(self.manager, browser)
        expected_file_actions = [
            {u'id': u'oneoffixx_retry',
             u'title': u'Oneoffixx retry',
             u'icon': u''},
            {u'id': u'trash_context',
             u'title': u'Trash',
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
        self.assertNotIn(
            {u'id': u'open_as_pdf', u'title': u'Open as PDF', u'icon': u''},
            self.get_file_actions(browser, self.document)
        )

    @browsing
    def test_oc_view_available_if_document_has_file(self, browser):
        self.login(self.regular_user, browser)
        self.assertIn(
            {u'id': u'oc_view', u'title': u'View', u'icon': u''},
            self.get_file_actions(browser, self.document)
        )

    @browsing
    def test_oc_view_not_available_if_document_has_no_file(self, browser):
        self.login(self.regular_user, browser)
        self.assertNotIn(
            {u'id': u'oc_view', u'title': u'View', u'icon': u''},
            self.get_file_actions(browser, self.empty_document)
        )

    @browsing
    def test_oc_view_not_available_if_document_is_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)
        self.assertNotIn(
            {u'id': u'oc_view', u'title': u'View', u'icon': u''},
            self.get_file_actions(browser, self.document)
        )


class TestTrashingActionsForDocuments(FileActionsTestBase):

    @browsing
    def test_trashing_available_for_document(self, browser):
        self.login(self.regular_user, browser)
        self.assertIn(
            {
                u'id': u'trash_context',
                u'title': u'Trash',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_untrashing_available_for_trashed_document(self, browser):
        self.login(self.regular_user, browser)

        trasher = ITrasher(self.document)
        trasher.trash()

        self.assertIn(
            {
                u'id': u'untrash_context',
                u'title': u'Untrash',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )


class TestFileActionsGetForTemplates(FileActionsTestBase):

    @browsing
    def test_available_file_actions(self, browser):
        self.login(self.dossier_responsible, browser)

        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'oc_direct_checkout', u'title': u'Checkout and edit'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'}
        ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, self.normal_template))


class TestFileActionsGetForDossierTemplateDocuments(FileActionsTestBase):

    @browsing
    def test_available_file_actions_for_dossier_template_document(self, browser):
        self.login(self.dossier_responsible, browser)

        template = create(Builder('document')
                          .within(self.dossiertemplate)
                          .titled(u'Werkst\xe4tte')
                          .with_dummy_content())

        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'oc_direct_checkout', u'title': u'Checkout and edit'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'}
        ]
        self.assertEqual(expected_file_actions,
                         self.get_file_actions(browser, template))

    @browsing
    def test_available_file_actions_for_subdossier_template_document(self, browser):
        self.login(self.dossier_responsible, browser)

        template = create(Builder('document')
                          .within(self.subdossiertemplate)
                          .titled(u'Werkst\xe4tte')
                          .with_dummy_content())

        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'oc_direct_checkout', u'title': u'Checkout and edit'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'},
        ]

        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, template),
        )


class TestFileActionsGetForProposalTemplates(FileActionsTestBase):

    @browsing
    def test_available_file_actions_for_proposal_template(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_file_actions = [
            {u'icon': u'', u'id': u'oc_view', u'title': u'View'},
            {u'icon': u'', u'id': u'oc_direct_checkout', u'title': u'Checkout and edit'},
            {u'icon': u'', u'id': u'download_copy', u'title': u'Download copy'},
            {u'icon': u'', u'id': u'open_as_pdf', u'title': u'Open as PDF'},
        ]

        self.assertListEqual(
            expected_file_actions,
            self.get_file_actions(browser, self.proposal_template),
        )


class TestNewTaskFromDocumentAction(FileActionsTestBase):

    @browsing
    def test_task_from_doc_not_available_for_doc_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-resolve',
                     data={'_authenticator': createToken()})
        self.assertNotIn(
            {
                u'id': u'new_task_from_document',
                u'title': u'New task from document',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.resolvable_document),
        )

    @browsing
    def test_task_from_doc_available_for_doc_in_task(self, browser):
        self.login(self.regular_user, browser)
        self.assertIn(
            {
                u'id': u'new_task_from_document',
                u'title': u'New task from document',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.taskdocument),
        )

    @browsing
    def test_task_from_doc_not_available_for_doc_in_inbox(self, browser):
        self.login(self.secretariat_user, browser)
        self.assertNotIn(
            {
                u'id': u'new_task_from_document',
                u'title': u'New task from document',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.inbox_document),
        )

    @browsing
    def test_task_from_doc_not_available_for_doc_in_private_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assertNotIn(
            {
                u'id': u'new_task_from_document',
                u'title': u'New task from document',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.private_document),
        )

    @browsing
    def test_task_from_doc_not_available_for_doc_in_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assertNotIn(
            {
                u'id': u'new_task_from_document',
                u'title': u'New task from document',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.inactive_document),
        )


class TestUnlockAction(FileActionsTestBase):

    @browsing
    def test_unlock_available_if_document_is_locked_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()

        self.assertIn(
            {
                u'id': u'unlock',
                u'title': u'Unlock',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_unlock_not_available_if_document_is_locked_by_another_user(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        self.login(self.dossier_responsible, browser)

        self.assertNotIn(
            {
                u'id': u'unlock',
                u'title': u'Unlock',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_unlock_available_for_manager(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        self.login(self.manager, browser)

        self.assertIn(
            {
                u'id': u'unlock',
                u'title': u'Unlock',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )

    @browsing
    def test_unlock_available_if_document_is_locked_by_workspace_lock(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock(COPIED_TO_WORKSPACE_LOCK)
        self.login(self.dossier_responsible, browser)

        self.assertIn(
            {
                u'id': u'unlock',
                u'title': u'Unlock',
                u'icon': u'',
            },
            self.get_file_actions(browser, self.document),
        )


class TestFolderButtons(FolderActionsTestBase):

    features = ('bumblebee', 'meeting')
    createTaskAction = {
        u'id': u'create_task',
        u'title': u'Create task',
        u'icon': u''}
    createForwardingAction = {
        u'id': u'create_forwarding',
        u'title': u'Forward',
        u'icon': u''}

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

    @browsing
    def test_create_proposal_not_available_if_meeting_feature_disabled(self, browser):
        self.deactivate_feature('meeting')
        self.login(self.secretariat_user, browser)
        self.assertNotIn({u'icon': u'', u'id': u'create_proposal', u'title': u'Create proposal'},
                         self.get_folder_buttons(browser, self.resolvable_dossier))

    @browsing
    def test_create_forwarding_not_available_for_workspace_document(self, browser):
        self.login(self.workspace_member, browser)
        self.assertNotIn(self.createForwardingAction,
                         self.get_folder_buttons(browser, self.workspace_document))

    @browsing
    def test_create_forwarding_available_for_inbox_document(self, browser):
        self.login(self.secretariat_user, browser)
        self.assertIn(self.createForwardingAction,
                      self.get_folder_buttons(browser, self.inbox_document))

    @browsing
    def test_folder_buttons_for_dossier(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'create_task', u'title': u'Create task'},
            {u'icon': u'', u'id': u'create_proposal', u'title': u'Create proposal'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'', u'id': u'checkin_with_comment', u'title': u'Check in with comment'},
            {u'icon': u'', u'id': u'checkin_without_comment', u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'submit_additional_documents',
                u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'trash_content', u'title': u'Move to trash'},
            {u'icon': u'', u'id': u'untrash_content', u'title': u'Restore from trash'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.dossier),
        )

    @browsing
    def test_folder_buttons_for_inactive_dossier(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.inactive_dossier),
        )

    @browsing
    def test_folder_buttons_for_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()

        self.login(self.regular_user, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.resolvable_dossier),
        )

    @browsing
    def test_folder_buttons_for_repository_folders(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'submit_additional_documents',
                u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.leaf_repofolder),
        )

    @browsing
    def test_folder_buttons_for_repository_folders_for_admins(self, browser):
        self.login(self.administrator, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'submit_additional_documents',
                u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.leaf_repofolder),
        )

        expected_folder_buttons.remove({u'icon': u'', u'id': u'delete', u'title': u'Delete'})

        self.login(self.limited_admin, browser)
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.leaf_repofolder),
        )

    @browsing
    def test_folder_buttons_for_repository_root(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'submit_additional_documents',
                u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.repository_root),
        )

    @browsing
    def test_folder_buttons_for_repository_root_for_admins(self, browser):
        self.login(self.administrator, browser)

        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'submit_additional_documents',
                u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.repository_root),
        )

        self.login(self.limited_admin, browser)
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.repository_root),
        )


class TestFolderActions(IntegrationTestCase):

    def get_folder_actions(self, browser, context):
        browser.open(context.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        return browser.json['folder_actions']

    @browsing
    def test_folder_actions_for_dossier(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_actions = [{u'icon': u'', u'id': u'edit_items', u'title': u'Edit metadata'}]

        self.assertListEqual(
            expected_folder_actions,
            self.get_folder_actions(browser, self.dossier),
        )

    @browsing
    def test_folder_actions_for_repository_folders(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_actions = [{u'icon': u'', u'id': u'edit_items', u'title': u'Edit metadata'}]

        self.assertListEqual(
            expected_folder_actions,
            self.get_folder_actions(browser, self.leaf_repofolder),
        )

    @browsing
    def test_folder_actions_for_repository_root(self, browser):
        self.login(self.regular_user, browser)

        expected_folder_actions = [{u'icon': u'', u'id': u'edit_items', u'title': u'Edit metadata'}]

        self.assertListEqual(
            expected_folder_actions,
            self.get_folder_actions(browser, self.repository_root),
        )

    @browsing
    def test_folder_actions_for_workspace(self, browser):
        self.login(self.workspace_member, browser)

        expected_folder_actions = [
            {u'icon': u'', u'id': u'edit_items', u'title': u'Edit metadata'},
            {u'icon': u'', u'id': u'delete_workspace_content', u'title': u'Delete'}
        ]

        self.assertListEqual(
            expected_folder_actions,
            self.get_folder_actions(browser, self.workspace),
        )


class TestWorkspaceClientFolderActions(FunctionalWorkspaceClientTestCase):

    list_workspaces_action = {
        u'id': u'list_workspaces',
        u'title': u'List workspaces',
        u'icon': u''}

    link_to_workspace_action = {
        u'id': u'link_to_workspace',
        u'title': u'Link to workspace',
        u'icon': u''}

    copy_documents_to_workspace_action = {
        u'id': u'copy_documents_to_workspace',
        u'title': u'Copy documents to workspace',
        u'icon': u''}

    copy_documents_from_workspace_action = {
        u'id': u'copy_documents_from_workspace',
        u'title': u'Copy back documents from workspace',
        u'icon': u''}

    create_linked_workspace_action = {
        u'id': u'create_linked_workspace',
        u'title': u'Create workspace',
        u'icon': u''}

    unlink_workspace_action = {
        u'id': u'unlink_workspace',
        u'title': u'Unlink workspace',
        u'icon': u''}

    workspace_actions = [list_workspaces_action,
                         link_to_workspace_action,
                         copy_documents_to_workspace_action,
                         copy_documents_from_workspace_action,
                         create_linked_workspace_action,
                         unlink_workspace_action]

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
    def test_only_copy_to_workspace_and_list_workspaces_available_in_subdossier(self, browser):
        browser.login()
        subdossier = create(Builder('dossier').within(self.dossier))
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            self.assert_workspace_actions(browser, subdossier,
                                          [self.list_workspaces_action,
                                           self.copy_documents_to_workspace_action])

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
    def test_link_to_workspace_action_only_available_if_linking_activated(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            actions = self.get_actions(browser, self.dossier)
            self.assertIn(self.link_to_workspace_action, actions)

            self.enable_linking(False)
            transaction.commit()

            actions = self.get_actions(browser, self.dossier)
            self.assertNotIn(self.link_to_workspace_action, actions)

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

            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-deactivate')
            transaction.commit()

            self.assert_workspace_actions(browser, self.dossier,
                                          [self.list_workspaces_action,
                                           self.unlink_workspace_action])

    @browsing
    def test_unlink_actions_available_in_dossier_with_linked_workspaces(self, browser):
        browser.login()
        with self.workspace_client_env():
            self.link_workspace(self.dossier)
            actions = self.get_actions(browser, self.dossier)
            self.assertIn(self.unlink_workspace_action, actions)

    @browsing
    def test_unlink_action_not_available_in_dossier_without_linked_workspaces(self, browser):
        browser.login()
        with self.workspace_client_env():
            actions = self.get_actions(browser, self.dossier)
            self.assertNotIn(self.unlink_workspace_action, actions)


class TestObjectButtonsGetForDocuments(ObjectButtonsTestBase):

    @browsing
    def test_document_does_not_have_delete_object_button(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
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
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
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
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
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
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.inactive_document),
        )

    @browsing
    def test_object_buttons_for_document_in_workspace(self, browser):
        self.login(self.workspace_member, browser)

        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
            {u'icon': u'', u'id': u'share_content', u'title': u'Share content'}]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.workspace_document),
        )

    @browsing
    def test_actions_for_document_in_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)

        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
            {u'icon': u'', u'id': u'share_content', u'title': u'Share content'}
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.workspace_folder_document),
        )

    @browsing
    def test_object_buttons_for_trashed_document_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})

        expected_object_buttons = [
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
            {u'icon': u'', u'id': u'share_content', u'title': u'Share content'},
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.workspace_document),
        )

    @browsing
    def test_actions_for_trashed_document_in_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_folder_document.absolute_url() + '/@trash',
                     method='POST', headers={'Accept': 'application/json'})

        expected_object_buttons = [
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
            {u'icon': u'', u'id': u'share_content', u'title': u'Share content'},
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.workspace_folder_document),
        )


class TestObjectButtonsGetForTemplates(ObjectButtonsTestBase):

    @browsing
    def test_available_object_button_actions_for_template_document(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.normal_template),
        )


class TestObjectButtonsGetForDossierTemplateDocuments(ObjectButtonsTestBase):

    @browsing
    def test_available_object_button_actions_for_dossier_template_document(self, browser):
        self.login(self.dossier_responsible, browser)

        template = create(Builder('document')
                          .within(self.dossiertemplate)
                          .titled(u'Werkst\xe4tte')
                          .with_dummy_content())

        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, template),
        )

    @browsing
    def test_available_object_button_actions_for_subdossier_template_document(self, browser):
        self.login(self.dossier_responsible, browser)

        template = create(Builder('document')
                          .within(self.subdossiertemplate)
                          .titled(u'Werkst\xe4tte')
                          .with_dummy_content())

        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'},
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, template),
        )


class TestObjectButtonsGetForProposalTemplates(ObjectButtonsTestBase):

    @browsing
    def test_available_object_button_actions_for_proposal_template(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'checkout_document', u'title': u'Checkout'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'copy_item', u'title': u'Copy item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'}
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.proposal_template),
        )


class TestObjectButtonsGetForProposals(ObjectButtonsTestBase):

    features = ('meeting',)

    @browsing
    def test_available_object_button_actions_for_proposals(self, browser):
        self.login(self.meeting_user, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'create_task_from_proposal',
             u'title': u'Create task from proposal'},
            {u'icon': u'', u'id': u'submit_additional_documents',
             u'title': u'Submit additional documents'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'}
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.proposal),
        )


class TestObjectButtonsGetForTasksAndForwardings(ObjectButtonsTestBase):

    @browsing
    def test_available_object_button_actions_for_tasks(self, browser):
        self.login(self.regular_user, browser)
        expected_object_buttons = [
            {u'icon': u'', u'id': u'zipexport', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'move_item', u'title': u'Move item'},
            {u'icon': u'', u'id': u'properties', u'title': u'Properties'}
        ]

        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.task),
        )

    @browsing
    def test_available_object_button_actions_for_forwardings(self, browser):
        self.login(self.secretariat_user, browser)
        expected_object_buttons = [
            {u'title': u'Export as Zip', u'id': u'zipexport', u'icon': u''},
            {u'title': u'Properties', u'id': u'properties', u'icon': u''}
        ]
        self.assertListEqual(
            expected_object_buttons,
            self.get_object_buttons(browser, self.inbox_forwarding),
        )


class TestFolderButtonsGetForTemplatesFolder(FolderActionsTestBase):

    @browsing
    def test_available_folder_button_actions_for_template_folder(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'', u'id': u'checkin_with_comment', u'title': u'Check in with comment'},
            {u'icon': u'', u'id': u'checkin_without_comment', u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'folder_delete_confirmation', u'title': u'Delete'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.templates),
        )

    @browsing
    def test_available_folder_button_actions_for_subtemplate_folder(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'', u'id': u'checkin_with_comment', u'title': u'Check in with comment'},
            {u'icon': u'', u'id': u'checkin_without_comment', u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'folder_delete_confirmation', u'title': u'Delete'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.subtemplates),
        )


class TestFolderButtonsGetForDossierTemplatesFolder(FolderActionsTestBase):

    @browsing
    def test_available_folder_button_actions_for_dossier_template_folder(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'', u'id': u'checkin_with_comment', u'title': u'Check in with comment'},
            {u'icon': u'', u'id': u'checkin_without_comment', u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'folder_delete_confirmation', u'title': u'Delete'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.dossiertemplate),
        )

    @browsing
    def test_available_folder_button_actions_for_subdossier_template_folder(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'delete', u'title': u'Delete'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'', u'id': u'checkin_with_comment', u'title': u'Check in with comment'},
            {u'icon': u'', u'id': u'checkin_without_comment', u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'folder_delete_confirmation', u'title': u'Delete'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'pdf_dossierlisting', u'title': u'Print selection (PDF)'},
            {u'icon': u'', u'id': u'pdf_taskslisting', u'title': u'Print selection (PDF)'}
        ]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.subdossiertemplate),
        )


class TestFolderButtonsGetForWorkspace(FolderActionsTestBase):

    @browsing
    def test_available_folder_button_actions_for_workspace(self, browser):
        self.login(self.workspace_member, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'',
             u'id': u'checkin_with_comment',
             u'title': u'Check in with comment'},
            {u'icon': u'',
             u'id': u'checkin_without_comment',
             u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'trash_content', u'title': u'Move to trash'},
            {u'icon': u'', u'id': u'untrash_content', u'title': u'Restore from trash'},
            {u'icon': u'',
             u'id': u'pdf_dossierlisting',
             u'title': u'Print selection (PDF)'},
            {u'icon': u'',
             u'id': u'pdf_taskslisting',
             u'title': u'Print selection (PDF)'}
        ]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.workspace),
        )

    @browsing
    def test_available_folder_button_actions_for_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)
        expected_folder_buttons = [
            {u'icon': u'', u'id': u'rename', u'title': u'Rename'},
            {u'icon': u'', u'id': u'zip_selected', u'title': u'Export as Zip'},
            {u'icon': u'', u'id': u'export_tasks', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'export_proposals', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'copy_items', u'title': u'Copy items'},
            {u'icon': u'', u'id': u'send_as_email', u'title': u'Send as email'},
            {u'icon': u'', u'id': u'attach_documents', u'title': u'Attach to email'},
            {u'icon': u'', u'id': u'checkout', u'title': u'Check out'},
            {u'icon': u'', u'id': u'cancel', u'title': u'Cancel'},
            {u'icon': u'',
             u'id': u'checkin_with_comment',
             u'title': u'Check in with comment'},
            {u'icon': u'',
             u'id': u'checkin_without_comment',
             u'title': u'Check in without comment'},
            {u'icon': u'', u'id': u'export_documents', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'delete_participants', u'title': u'Delete'},
            {u'icon': u'', u'id': u'add_participant', u'title': u'Add participant'},
            {u'icon': u'', u'id': u'move_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'move_proposal_items', u'title': u'Move items'},
            {u'icon': u'', u'id': u'export_dossiers', u'title': u'Export selection'},
            {u'icon': u'', u'id': u'trash_content', u'title': u'Move to trash'},
            {u'icon': u'', u'id': u'untrash_content', u'title': u'Restore from trash'},
            {u'icon': u'',
             u'id': u'pdf_dossierlisting',
             u'title': u'Print selection (PDF)'},
            {u'icon': u'',
             u'id': u'pdf_taskslisting',
             u'title': u'Print selection (PDF)'}
        ]

        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.workspace_folder),
        )

        ITrasher(self.workspace_folder).trash()
        expected_folder_buttons.remove({u'icon': u'', u'id': u'trash_content', u'title': u'Move to trash'})
        expected_folder_buttons.remove({u'icon': u'', u'id': u'untrash_content', u'title': u'Restore from trash'})
        self.assertListEqual(
            expected_folder_buttons,
            self.get_folder_buttons(browser, self.workspace_folder),
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


class TestUIContextActionsGetForDossiers(UIContextActionsTestBase):

    @browsing
    def test_available_ui_context_actions_for_dossier_as_dossier_responsible(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_ui_context_actions = []
        self.assertListEqual(
            expected_ui_context_actions,
            self.get_ui_context_actions(browser, self.dossier),
        )

    @browsing
    def test_available_ui_context_actions_for_dossier_as_dossier_manager(self, browser):
        self.login(self.dossier_manager, browser)
        expected_ui_context_actions = [
            {u'icon': u'', u'id': u'protect_dossier', u'title': u'Protect dossier'},
        ]
        self.assertListEqual(
            expected_ui_context_actions,
            self.get_ui_context_actions(browser, self.dossier),
        )


class TestUIContextActionsGetForWorkspaces(UIContextActionsTestBase):

    @browsing
    def test_available_ui_context_actions_for_workspace_as_admin(self, browser):
        self.login(self.administrator, browser)
        expected_ui_context_actions = []
        self.assertListEqual(
            expected_ui_context_actions,
            self.get_ui_context_actions(browser, self.workspace),
        )

    @browsing
    def test_available_ui_context_actions_for_inactive_workspace_as_admin(self, browser):
        self.login(self.administrator, browser)
        api.content.transition(
            self.workspace,
            'opengever_workspace--TRANSITION--deactivate--active_inactive')

        expected_ui_context_actions = [
            {u'icon': u'', u'id': u'delete_workspace', u'title': u'Delete'},
        ]
        self.assertListEqual(
            expected_ui_context_actions,
            self.get_ui_context_actions(browser, self.workspace),
        )

    @browsing
    def test_available_ui_context_actions_for_linked_inactive_workspace_as_admin(self, browser):
        self.login(self.administrator, browser)
        self.workspace.external_reference = u'a dossier UID'
        api.content.transition(
            self.workspace,
            'opengever_workspace--TRANSITION--deactivate--active_inactive')

        expected_ui_context_actions = []
        self.assertListEqual(
            expected_ui_context_actions,
            self.get_ui_context_actions(browser, self.workspace),
        )
