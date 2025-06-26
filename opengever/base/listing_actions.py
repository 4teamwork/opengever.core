from opengever.base.interfaces import IDeleter
from opengever.base.interfaces import IListingActions
from zope.interface import implementer


@implementer(IListingActions)
class BaseListingActions(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_actions(self):
        self.actions = []
        self.maybe_add_edit_items()
        self.maybe_add_change_items_state()
        self.maybe_add_close_tasks()
        self.maybe_add_attach_documents()
        self.maybe_add_copy_items()
        self.maybe_add_move_items()
        self.maybe_add_create_task()
        self.maybe_add_create_proposal()
        self.maybe_add_create_forwarding()
        self.maybe_add_zip_selected()
        self.maybe_add_export_documents()
        self.maybe_add_export_dossiers()
        self.maybe_add_export_dossiers_with_subdossiers()
        self.maybe_add_export_tasks()
        self.maybe_add_export_proposals()
        self.maybe_add_pdf_dossierlisting()
        self.maybe_add_pdf_taskslisting()
        self.maybe_add_create_disposition()
        self.maybe_add_copy_documents_to_workspace()
        self.maybe_add_copy_dossier_to_workspace()
        self.maybe_add_trash_content()
        self.maybe_add_untrash_content()
        self.maybe_add_remove()
        self.maybe_add_delete_workspace_content()
        self.maybe_add_delete()
        self.maybe_add_export_users()
        self.maybe_add_transfer_dossier_responsible()
        return self.actions

    def add_action(self, action):
        self.actions.append(action)

    def is_attach_documents_available(self):
        return False

    def is_copy_documents_to_workspace_available(self):
        return False

    def is_copy_dossier_to_workspace_available(self):
        return False

    def is_copy_items_available(self):
        return False

    def is_create_disposition_available(self):
        return False

    def is_create_forwarding_available(self):
        return False

    def is_create_proposal_available(self):
        return False

    def is_create_task_available(self):
        return False

    def is_delete_available(self):
        return IDeleter(self.context).is_delete_allowed()

    def is_delete_workspace_content_available(self):
        return False

    def is_edit_items_available(self):
        return False

    def is_change_items_state_available(self):
        return False

    def is_close_tasks_available(self):
        return False

    def is_export_documents_available(self):
        return False

    def is_export_dossiers_available(self):
        return False

    def is_export_dossiers_with_subdossiers_available(self):
        return False

    def is_export_proposals_available(self):
        return False

    def is_export_tasks_available(self):
        return False

    def is_move_items_available(self):
        return False

    def is_pdf_dossierlisting_available(self):
        return False

    def is_pdf_taskslisting_available(self):
        return False

    def is_remove_available(self):
        return False

    def is_trash_content_available(self):
        return False

    def is_untrash_content_available(self):
        return False

    def is_zip_selected_available(self):
        return False

    def is_export_users_available(self):
        return False

    def is_transfer_dossier_responsible_available(self):
        return False

    def maybe_add_attach_documents(self):
        if self.is_attach_documents_available():
            self.add_action(u'attach_documents')

    def maybe_add_copy_documents_to_workspace(self):
        if self.is_copy_documents_to_workspace_available():
            self.add_action(u'copy_documents_to_workspace')

    def maybe_add_copy_dossier_to_workspace(self):
        if self.is_copy_dossier_to_workspace_available():
            self.add_action(u'copy_dossier_to_workspace')

    def maybe_add_copy_items(self):
        if self.is_copy_items_available():
            self.add_action(u'copy_items')

    def maybe_add_create_disposition(self):
        if self.is_create_disposition_available():
            self.add_action(u'create_disposition')

    def maybe_add_create_forwarding(self):
        if self.is_create_forwarding_available():
            self.add_action(u'create_forwarding')

    def maybe_add_create_proposal(self):
        if self.is_create_proposal_available():
            self.add_action(u'create_proposal')

    def maybe_add_create_task(self):
        if self.is_create_task_available():
            self.add_action(u'create_task')

    def maybe_add_delete(self):
        if self.is_delete_available():
            self.add_action(u'delete')

    def maybe_add_delete_workspace_content(self):
        if self.is_delete_workspace_content_available():
            self.add_action(u'delete_workspace_content')

    def maybe_add_edit_items(self):
        if self.is_edit_items_available():
            self.add_action(u'edit_items')

    def maybe_add_change_items_state(self):
        if self.is_change_items_state_available():
            self.add_action(u'change_items_state')

    def maybe_add_close_tasks(self):
        if self.is_close_tasks_available():
            self.add_action(u'close_tasks')

    def maybe_add_export_documents(self):
        if self.is_export_documents_available():
            self.add_action(u'export_documents')

    def maybe_add_export_dossiers(self):
        if self.is_export_dossiers_available():
            self.add_action(u'export_dossiers')

    def maybe_add_export_dossiers_with_subdossiers(self):
        if self.is_export_dossiers_with_subdossiers_available():
            self.add_action(u'export_dossiers_with_subdossiers')

    def maybe_add_export_proposals(self):
        if self.is_export_proposals_available():
            self.add_action(u'export_proposals')

    def maybe_add_export_tasks(self):
        if self.is_export_tasks_available():
            self.add_action(u'export_tasks')

    def maybe_add_move_items(self):
        if self.is_move_items_available():
            self.add_action(u'move_items')

    def maybe_add_pdf_dossierlisting(self):
        if self.is_pdf_dossierlisting_available():
            self.add_action(u'pdf_dossierlisting')

    def maybe_add_pdf_taskslisting(self):
        if self.is_pdf_taskslisting_available():
            self.add_action(u'pdf_taskslisting')

    def maybe_add_remove(self):
        if self.is_remove_available():
            self.add_action(u'remove')

    def maybe_add_trash_content(self):
        if self.is_trash_content_available():
            self.add_action(u'trash_content')

    def maybe_add_untrash_content(self):
        if self.is_untrash_content_available():
            self.add_action(u'untrash_content')

    def maybe_add_zip_selected(self):
        if self.is_zip_selected_available():
            self.add_action(u'zip_selected')

    def maybe_add_export_users(self):
        if self.is_export_users_available():
            self.add_action(u'export_users')

    def maybe_add_transfer_dossier_responsible(self):
        if self.is_transfer_dossier_responsible_available():
            self.add_action(u'transfer_dossier_responsible')
