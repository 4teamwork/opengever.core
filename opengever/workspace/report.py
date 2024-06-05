from opengever.globalindex.browser.report import UserReport


class WorkspaceParticipantsReport(UserReport):
    """View that generate an excel spreadsheet which list all selected users
    """
    filename = "workspace_participants_report.xlsx"

    def check_permissions(self):
        pass
