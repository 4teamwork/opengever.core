from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IDeleter
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.trash.trash import ITrasher
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.interfaces import IWorkspaceMeeting
from opengever.workspace.utils import get_containing_workspace
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from zExceptions import Forbidden
from zope.component import adapter


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class WorkspaceFolderListingActions(BaseListingActions):

    def is_copy_items_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_zip_selected_available(self):
        return True

    def is_trash_content_available(self):
        return api.user.has_permission('opengever.trash: Trash content', obj=self.context)


@adapter(IToDo, IOpengeverBaseLayer)
class TodoContextActions(BaseContextActions):

    def is_share_content_available(self):
        return get_containing_workspace(self.context).access_members_allowed()

    def is_edit_available(self):
        return api.user.has_permission('Modify portal content', obj=self.context)


@adapter(IWorkspaceMeeting, IOpengeverBaseLayer)
class WorkspaceMeetingContextActions(BaseContextActions):

    def is_meeting_ical_download_available(self):
        return True

    def is_meeting_minutes_pdf_available(self):
        return True

    def is_share_content_available(self):
        return get_containing_workspace(self.context).access_members_allowed()

    def is_add_save_minutes_as_pdf_available(self):
        return True


@adapter(IWorkspace, IOpengeverBaseLayer)
class WorkspaceContextActions(BaseContextActions):

    def is_add_invitation_available(self):
        return api.user.has_permission('Sharing page: Delegate WorkspaceAdmin role',
                                       obj=self.context)

    def is_delete_workspace_available(self):
        return self.context.is_deletion_allowed()

    def is_share_content_available(self):
        return get_containing_workspace(self.context).access_members_allowed()

    def is_zipexport_available(self):
        return not is_restricted_workspace_and_guest(self.context)


@adapter(IWorkspaceFolder, IOpengeverBaseLayer)
class WorkspaceFolderContextActions(BaseContextActions):

    def is_delete_available(self):
        return False

    def is_delete_workspace_context_available(self):
        try:
            IDeleter(self.context).verify_may_delete()
            return True
        except Forbidden:
            return False

    def is_edit_available(self):
        if ITrasher(self.context).is_trashed():
            return False
        return super(WorkspaceFolderContextActions, self).is_edit_available()

    def is_share_content_available(self):
        return get_containing_workspace(self.context).access_members_allowed()

    def is_trash_context_available(self):
        return ITrasher(self.context).verify_may_trash(raise_on_violations=False)

    def is_untrash_context_available(self):
        return ITrasher(self.context).verify_may_untrash(raise_on_violations=False)

    def is_zipexport_available(self):
        return not is_restricted_workspace_and_guest(self.context)
