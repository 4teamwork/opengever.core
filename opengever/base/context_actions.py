from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IDeleter
from plone import api
from zope.interface import implementer


@implementer(IContextActions)
class BaseContextActions(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_actions(self):
        self.actions = []
        self.maybe_add_add_dossier_transfer()
        self.maybe_add_add_invitation()
        self.maybe_add_attach_to_email()
        self.maybe_add_cancel_checkout()
        self.maybe_add_checkin_with_comment()
        self.maybe_add_checkin_without_comment()
        self.maybe_add_checkout_document()
        self.maybe_add_copy_documents_from_workspace()
        self.maybe_add_copy_documents_to_workspace()
        self.maybe_add_copy_item()
        self.maybe_add_create_forwarding()
        self.maybe_add_create_linked_workspace()
        self.maybe_add_create_task_from_proposal()
        self.maybe_add_delete()
        self.maybe_add_delete_repository()
        self.maybe_add_delete_workspace()
        self.maybe_add_delete_workspace_context()
        self.maybe_add_docugate_retry()
        self.maybe_add_document_from_docugate()
        self.maybe_add_document_with_oneoffixx_template()
        self.maybe_add_document_with_template()
        self.maybe_add_dossier_with_template()
        self.maybe_add_download_appraisal_list()
        self.maybe_add_download_copy()
        self.maybe_add_download_excel()
        self.maybe_add_download_removal_protocol()
        self.maybe_add_download_sip()
        self.maybe_add_edit()
        self.maybe_add_edit_public_trial_status()
        self.maybe_add_export_pdf()
        self.maybe_add_link_to_workspace()
        self.maybe_add_list_workspaces()
        self.maybe_add_local_roles()
        self.maybe_add_meeting_ical_download()
        self.maybe_add_meeting_minutes_pdf()
        self.maybe_add_move_item()
        self.maybe_add_new_task_from_document()
        self.maybe_add_oc_direct_checkout()
        self.maybe_add_oc_direct_edit()
        self.maybe_add_oc_view()
        self.maybe_add_office_online_edit()
        self.maybe_add_oneoffixx_retry()
        self.maybe_add_open_as_pdf()
        self.maybe_add_pdf_dossierdetails()
        self.maybe_add_prefix_manager()
        self.maybe_add_protect_dossier()
        self.maybe_add_revive_bumblebee_preview()
        self.maybe_add_save_document_as_pdf()
        self.maybe_add_share_content()
        self.maybe_add_submit_additional_documents()
        self.maybe_add_trash_context()
        self.maybe_add_unlink_workspace()
        self.maybe_add_unlock()
        self.maybe_add_untrash_context()
        self.maybe_add_zipexport()
        self.maybe_add_save_minutes_as_pdf()
        self.maybe_export_workspace_user()
        return self.actions

    def add_action(self, action):
        self.actions.append(action)

    def is_add_invitation_available(self):
        return False

    def is_add_dossier_transfer_available(self):
        return False

    def is_attach_to_email_available(self):
        return False

    def is_cancel_checkout_available(self):
        return False

    def is_checkin_with_comment_available(self):
        return False

    def is_checkin_without_comment_available(self):
        return False

    def is_checkout_document_available(self):
        return False

    def is_copy_documents_from_workspace_available(self):
        return False

    def is_copy_documents_to_workspace_available(self):
        return False

    def is_copy_item_available(self):
        return False

    def is_create_forwarding_available(self):
        return False

    def is_create_linked_workspace_available(self):
        return False

    def is_create_task_from_proposal_available(self):
        return False

    def is_delete_repository_available(self):
        return False

    def is_delete_available(self):
        return IDeleter(self.context).is_delete_allowed()

    def is_delete_workspace_available(self):
        return False

    def is_delete_workspace_context_available(self):
        return False

    def is_docugate_retry_available(self):
        return False

    def is_document_from_docugate_available(self):
        return False

    def is_document_with_oneoffixx_template_available(self):
        return False

    def is_document_with_template_available(self):
        return False

    def is_dossier_with_template_available(self):
        return False

    def is_download_appraisal_list_available(self):
        return False

    def is_download_copy_available(self):
        return False

    def is_download_excel_available(self):
        return False

    def is_download_removal_protocol_available(self):
        return False

    def is_download_sip_available(self):
        return False

    def is_edit_available(self):
        is_locked_for_current_user = self.context.restrictedTraverse(
            '@@plone_lock_info').is_locked_for_current_user()
        has_modify_permission = api.user.has_permission('Modify portal content', obj=self.context)
        return has_modify_permission and not is_locked_for_current_user

    def is_edit_public_trial_status_available(self):
        return False

    def is_export_pdf_available(self):
        return False

    def is_link_to_workspace_available(self):
        return False

    def is_list_workspaces_available(self):
        return False

    def is_local_roles_available(self):
        return api.user.has_permission('Sharing page: Delegate roles', obj=self.context)

    def is_meeting_ical_download_available(self):
        return False

    def is_meeting_minutes_pdf_available(self):
        return False

    def is_move_item_available(self):
        return False

    def is_new_task_from_document_available(self):
        return False

    def is_oc_direct_checkout_available(self):
        return False

    def is_oc_direct_edit_available(self):
        return False

    def is_oc_view_available(self):
        return False

    def is_office_online_edit_available(self):
        return False

    def is_oneoffixx_retry_available(self):
        return False

    def is_open_as_pdf_available(self):
        return False

    def is_pdf_dossierdetails_available(self):
        return False

    def is_prefix_manager_available(self):
        return False

    def is_protect_dossier_available(self):
        return False

    def is_revive_bumblebee_preview_available(self):
        return False

    def is_save_document_as_pdf_available(self):
        return False

    def is_share_content_available(self):
        return False

    def is_submit_additional_documents_available(self):
        return False

    def is_trash_context_available(self):
        return False

    def is_unlink_workspace_available(self):
        return False

    def is_unlock_available(self):
        return False

    def is_untrash_context_available(self):
        return False

    def is_zipexport_available(self):
        return False

    def is_add_save_minutes_as_pdf_available(self):
        return False

    def is_export_workspace_users_available(self):
        return False

    def maybe_add_add_invitation(self):
        if self.is_add_invitation_available():
            self.add_action(u'add_invitation')

    def maybe_add_attach_to_email(self):
        if self.is_attach_to_email_available():
            self.add_action(u'attach_to_email')

    def maybe_add_cancel_checkout(self):
        if self.is_cancel_checkout_available():
            self.add_action(u'cancel_checkout')

    def maybe_add_checkin_with_comment(self):
        if self.is_checkin_with_comment_available():
            self.add_action(u'checkin_with_comment')

    def maybe_add_checkin_without_comment(self):
        if self.is_checkin_without_comment_available():
            self.add_action(u'checkin_without_comment')

    def maybe_add_checkout_document(self):
        if self.is_checkout_document_available():
            self.add_action(u'checkout_document')

    def maybe_add_copy_documents_from_workspace(self):
        if self.is_copy_documents_from_workspace_available():
            self.add_action(u'copy_documents_from_workspace')

    def maybe_add_copy_documents_to_workspace(self):
        if self.is_copy_documents_to_workspace_available():
            self.add_action(u'copy_documents_to_workspace')

    def maybe_add_copy_item(self):
        if self.is_copy_item_available():
            self.add_action(u'copy_item')

    def maybe_add_create_forwarding(self):
        if self.is_create_forwarding_available():
            self.add_action(u'create_forwarding')

    def maybe_add_create_linked_workspace(self):
        if self.is_create_linked_workspace_available():
            self.add_action(u'create_linked_workspace')

    def maybe_add_create_task_from_proposal(self):
        if self.is_create_task_from_proposal_available():
            self.add_action(u'create_task_from_proposal')

    def maybe_add_document_from_docugate(self):
        if self.is_document_from_docugate_available():
            self.add_action(u'document_from_docugate')

    def maybe_add_document_with_oneoffixx_template(self):
        if self.is_document_with_oneoffixx_template_available():
            self.add_action(u'document_with_oneoffixx_template')

    def maybe_add_document_with_template(self):
        if self.is_document_with_template_available():
            self.add_action(u'document_with_template')

    def maybe_add_delete(self):
        if self.is_delete_available():
            self.add_action(u'delete')

    def maybe_add_delete_repository(self):
        if self.is_delete_repository_available():
            self.add_action(u'delete_repository')

    def maybe_add_delete_workspace(self):
        if self.is_delete_workspace_available():
            self.add_action(u'delete_workspace')

    def maybe_add_delete_workspace_context(self):
        if self.is_delete_workspace_context_available():
            self.add_action(u'delete_workspace_context')

    def maybe_add_docugate_retry(self):
        if self.is_docugate_retry_available():
            self.add_action(u'docugate_retry')

    def maybe_add_add_dossier_transfer(self):
        if self.is_add_dossier_transfer_available():
            self.add_action(u'add_dossier_transfer')

    def maybe_add_dossier_with_template(self):
        if self.is_dossier_with_template_available():
            self.add_action(u'dossier_with_template')

    def maybe_add_download_appraisal_list(self):
        if self.is_download_appraisal_list_available():
            self.add_action(u'download-appraisal-list')

    def maybe_add_download_copy(self):
        if self.is_download_copy_available():
            self.add_action(u'download_copy')

    def maybe_add_download_excel(self):
        if self.is_download_excel_available():
            self.add_action(u'download_excel')

    def maybe_add_download_removal_protocol(self):
        if self.is_download_removal_protocol_available():
            self.add_action(u'download-removal-protocol')

    def maybe_add_download_sip(self):
        if self.is_download_sip_available():
            self.add_action(u'download-sip')

    def maybe_add_edit(self):
        if self.is_edit_available():
            self.add_action(u'edit')

    def maybe_add_edit_public_trial_status(self):
        if self.is_edit_public_trial_status_available():
            self.add_action(u'edit-public-trial-status')

    def maybe_add_export_pdf(self):
        if self.is_export_pdf_available():
            self.add_action(u'export_pdf')

    def maybe_add_link_to_workspace(self):
        if self.is_link_to_workspace_available():
            self.add_action(u'link_to_workspace')

    def maybe_add_list_workspaces(self):
        if self.is_list_workspaces_available():
            self.add_action(u'list_workspaces')

    def maybe_add_local_roles(self):
        if self.is_local_roles_available():
            self.add_action(u'local_roles')

    def maybe_add_meeting_ical_download(self):
        if self.is_meeting_ical_download_available():
            self.add_action(u'meeting_ical_download')

    def maybe_add_meeting_minutes_pdf(self):
        if self.is_meeting_minutes_pdf_available():
            self.add_action(u'meeting_minutes_pdf')

    def maybe_add_move_item(self):
        if self.is_move_item_available():
            self.add_action(u'move_item')

    def maybe_add_new_task_from_document(self):
        if self.is_new_task_from_document_available():
            self.add_action(u'new_task_from_document')

    def maybe_add_oc_direct_checkout(self):
        if self.is_oc_direct_checkout_available():
            self.add_action(u'oc_direct_checkout')

    def maybe_add_oc_direct_edit(self):
        if self.is_oc_direct_edit_available():
            self.add_action(u'oc_direct_edit')

    def maybe_add_oc_view(self):
        if self.is_oc_view_available():
            self.add_action(u'oc_view')

    def maybe_add_office_online_edit(self):
        if self.is_office_online_edit_available():
            self.add_action(u'office_online_edit')

    def maybe_add_oneoffixx_retry(self):
        if self.is_oneoffixx_retry_available():
            self.add_action(u'oneoffixx_retry')

    def maybe_add_open_as_pdf(self):
        if self.is_open_as_pdf_available():
            self.add_action(u'open_as_pdf')

    def maybe_add_pdf_dossierdetails(self):
        if self.is_pdf_dossierdetails_available():
            self.add_action(u'pdf_dossierdetails')

    def maybe_add_prefix_manager(self):
        if self.is_prefix_manager_available():
            self.add_action(u'prefix_manager')

    def maybe_add_protect_dossier(self):
        if self.is_protect_dossier_available():
            self.add_action(u'protect_dossier')

    def maybe_add_share_content(self):
        if self.is_share_content_available():
            self.add_action(u'share_content')

    def maybe_add_submit_additional_documents(self):
        if self.is_submit_additional_documents_available():
            self.add_action(u'submit_additional_documents')

    def maybe_add_trash_context(self):
        if self.is_trash_context_available():
            self.add_action(u'trash_context')

    def maybe_add_unlink_workspace(self):
        if self.is_unlink_workspace_available():
            self.add_action(u'unlink_workspace')

    def maybe_add_untrash_context(self):
        if self.is_untrash_context_available():
            self.add_action(u'untrash_context')

    def maybe_add_revive_bumblebee_preview(self):
        if self.is_revive_bumblebee_preview_available():
            self.add_action(u'revive_bumblebee_preview')

    def maybe_add_save_document_as_pdf(self):
        if self.is_save_document_as_pdf_available():
            self.add_action(u'save_document_as_pdf')

    def maybe_add_unlock(self):
        if self.is_unlock_available():
            self.add_action(u'unlock')

    def maybe_add_zipexport(self):
        if self.is_zipexport_available():
            self.add_action(u'zipexport')

    def maybe_add_save_minutes_as_pdf(self):
        if self.is_add_save_minutes_as_pdf_available():
            self.add_action(u'save_minutes_as_pdf')

    def maybe_export_workspace_user(self):
        if self.is_export_workspace_users_available():
            self.add_action(u'export_workspace_participators')
