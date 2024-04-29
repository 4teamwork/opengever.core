from opengever.globalindex.browser.report import UserReport
from plone import api
from zExceptions import Unauthorized


class WorkSpaceUserReport (UserReport):
    """View that generate an Excel spreadsheet which list all selected workspace users"""

    filename = "workspace_user_report.xlsx"

    def check_permissions(self):
        if not api.user.has_permission('opengever.workspace.AccessAllUsersAndGroups', obj=self.context):
            raise Unauthorized
