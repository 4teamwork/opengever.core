from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.docugate import is_docugate_feature_enabled
from opengever.dossier.base import DOSSIER_STATE_RESOLVED
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossiertransfer import is_dossier_transfer_feature_enabled
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.workspaceclient import is_linking_enabled
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from zope.component import adapter


class DossierListingActions(BaseListingActions):

    def is_copy_items_available(self):
        return True

    def is_create_disposition_available(self):
        return api.user.has_permission('opengever.disposition: Add disposition')

    def is_edit_items_available(self):
        return True

    def is_change_items_state_available(self):
        return True

    def is_export_dossiers_available(self):
        return True

    def is_export_dossiers_with_subdossiers_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_pdf_dossierlisting_available(self):
        return True


class PrivateDossierListingActions(BaseListingActions):

    def is_edit_items_available(self):
        return True

    def is_change_items_state_available(self):
        return True

    def is_export_dossiers_available(self):
        return True

    def is_pdf_dossierlisting_available(self):
        return True


class DossierTemplateListingActions(BaseListingActions):

    def is_move_items_available(self):
        return True


@adapter(IDossierMarker, IOpengeverBaseLayer)
class SubDossierListingActions(DossierListingActions):

    def is_copy_dossier_to_workspace_available(self):
        if not self.context.is_open():
            return False
        if not is_workspace_client_feature_available():
            return False
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False
        if not api.user.has_permission('opengever.workspaceclient: Use Workspace Client'):
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_create_disposition_available(self):
        return False


@adapter(IDossierMarker, IOpengeverBaseLayer)
class DossierContextActions(BaseContextActions):

    def __init__(self, context, request):
        super(DossierContextActions, self).__init__(context, request)
        self.can_use_workspace_client = self._can_use_workspace_client()

    def _can_use_workspace_client(self):
        return (
            is_workspace_client_feature_available()
            and api.user.has_permission('opengever.workspaceclient: Use Workspace Client')
        )

    def is_add_dossier_transfer_available(self):
        return (
            is_dossier_transfer_feature_enabled()
            and api.user.has_permission('View', obj=self.context)
            and api.content.get_state(self.context) == DOSSIER_STATE_RESOLVED
        )

    def is_copy_documents_from_workspace_available(self):
        if not self.can_use_workspace_client:
            return False
        if not api.user.has_permission('Add portal content', obj=self.context):
            return False
        if self.context.is_subdossier():
            return False
        if not self.context.is_open():
            return False
        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_copy_documents_to_workspace_available(self):
        if not self.can_use_workspace_client:
            return False
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False
        if not self.context.is_open():
            return False
        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_create_linked_workspace_available(self):
        if not self.can_use_workspace_client:
            return False
        if self.context.is_subdossier():
            return False
        if not self.context.is_open():
            return False
        return api.user.has_permission('Modify portal content', obj=self.context)

    def is_document_from_docugate_available(self):
        return api.user.has_permission('Add portal content', obj=self.context) \
            and is_docugate_feature_enabled()

    def is_document_with_oneoffixx_template_available(self):
        return api.user.has_permission('Add portal content', obj=self.context) \
            and is_oneoffixx_feature_enabled()

    def is_document_with_template_available(self):
        return api.user.has_permission('Add portal content', obj=self.context)

    def is_export_pdf_available(self):
        return True

    def is_link_to_workspace_available(self):
        if not self.can_use_workspace_client:
            return False
        if self.context.is_subdossier():
            return False
        if not self.context.is_open():
            return False
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False
        return is_linking_enabled()

    def is_list_workspaces_available(self):
        return self.can_use_workspace_client

    def is_pdf_dossierdetails_available(self):
        return True

    def is_protect_dossier_available(self):
        return api.user.has_permission('opengever.dossier: Protect dossier', obj=self.context)

    def is_unlink_workspace_available(self):
        if not self.can_use_workspace_client:
            return False
        if self.context.is_subdossier():
            return False
        if not api.user.has_permission('opengever.workspaceclient: Unlink Workspace',
                                       obj=self.context):
            return False
        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_zipexport_available(self):
        return True


@adapter(IDossierTemplateMarker, IOpengeverBaseLayer)
class DossierTemplateContextActions(BaseContextActions):

    def is_move_item_available(self):
        return api.user.has_permission('Copy or Move', obj=self.context)
