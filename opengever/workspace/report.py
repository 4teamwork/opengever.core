from opengever.globalindex.browser.report import UserReport
from plone import api
from zExceptions import Unauthorized


class WorkspaceParticipantsReport(UserReport):
    """View that generate an excel spreadsheet which list all selected users
    """
    filename = "workspace_participants_report.xlsx"

    def check_permissions(self):
        if not api.user.has_permission(
            'opengever.workspace.AccessAllUsersAndGroups', obj=self.context
        ):
            raise Unauthorized
