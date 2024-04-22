from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IContextActions
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from zope.component import queryMultiAdapter


class TestMailContextActions(IntegrationTestCase):

    features = ('bumblebee', )

    def get_actions(self, context):
        adapter = queryMultiAdapter((context, self.request), interface=IContextActions)
        return adapter.get_actions() if adapter else []

    def test_context_actions_for_mail_in_dossier(self):
        self.login(self.regular_user)
        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'edit',
            u'move_item',
            u'new_task_from_document',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'trash_context',
            u'extract_attachments',
        ]

        self.assertEqual(expected_actions, self.get_actions(self.mail_eml))

    def test_context_actions_for_trashed_mail_in_dossier(self):
        self.login(self.regular_user)
        ITrasher(self.mail_eml).trash()
        expected_actions = [
            u'oc_view',
            u'revive_bumblebee_preview',
            u'untrash_context',
            u'extract_attachments',
        ]
        self.assertEqual(expected_actions, self.get_actions(self.mail_eml))

    def test_context_actions_for_mail_in_resolved_task(self):
        self.login(self.regular_user)
        mail = create(Builder('mail')
                      .within(self.subtask)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'edit',
            u'new_task_from_document',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'trash_context',
            u'extract_attachments',
        ]
        self.assertEqual(expected_actions, self.get_actions(mail))

    def test_returns_error_when_extraction_parent_is_not_open(self):
        self.login(self.regular_user)
        mail = create(Builder('mail')
                      .within(self.inactive_dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
        ]
        self.assertEqual(expected_actions, self.get_actions(mail))

    def test_mail_actions_in_workspace_with_guest(self):
        self.login(self.workspace_guest)

        expected_actions = [
            u'attach_to_email',
            u'copy_item',
            u'download_copy',
            u'move_item',
            u'oc_view',
            u'open_as_pdf',
            u'revive_bumblebee_preview',
            u'share_content']

        self.assertEqual(expected_actions,
                         self.get_actions(self.workspace_mail))

    def test_mail_actions_in_workspace_with_guest_restriction(self):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.login(self.workspace_guest)
        mail = create(Builder('document')
                      .within(self.workspace))

        expected_actions_restricted_guest = [u'revive_bumblebee_preview']
        self.assertEqual(expected_actions_restricted_guest, self.get_actions(mail))
