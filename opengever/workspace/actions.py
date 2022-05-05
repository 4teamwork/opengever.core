from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceMeeting
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from zope.component import adapter


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class WorkspaceFolderListingActions(BaseListingActions):

    def is_copy_items_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_trash_content_available(self):
        return api.user.has_permission('opengever.trash: Trash content', obj=self.context)


@adapter(IToDo, IOpengeverBaseLayer)
class TodoContextActions(BaseContextActions):

    def is_share_content_available(self):
        return True

    def is_edit_available(self):
        return api.user.has_permission('Modify portal content', obj=self.context)


@adapter(IWorkspaceMeeting, IOpengeverBaseLayer)
class WorkspaceMeetingContextActions(BaseContextActions):

    def is_meeting_ical_download_available(self):
        return True

    def is_meeting_minutes_pdf_available(self):
        return True

    def is_share_content_available(self):
        return True


@adapter(IWorkspace, IOpengeverBaseLayer)
class WorkspaceContextActions(BaseContextActions):

    def is_add_invitation_available(self):
        return api.user.has_permission('Sharing page: Delegate WorkspaceAdmin role',
                                       obj=self.context)

    def is_delete_workspace_available(self):
        return self.context.is_deletion_allowed()

    def is_share_content_available(self):
        return True
