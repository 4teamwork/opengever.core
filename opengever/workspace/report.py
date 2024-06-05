from opengever.globalindex.browser.report import UserReport
from plone import api
from zExceptions import Unauthorized


class WorkspaceParticipantsReport(UserReport):
    """View that generate an excel spreadsheet which list all selected users
    """
    filename = "workspace_participants_report.xlsx"

    def check_permissions(self):

        all_users_and_group_permission = api.user.has_permission(
            'opengever.workspace: Access all users and groups', obj=self.context
        )
        workspace_admin_permission = api.user.has_permission(
            'Sharing page: Delegate WorkspaceAdmin role', obj=self.context
        )
        if not all_users_and_group_permission or not workspace_admin_permission:
            raise Unauthorized
