from ftw.upgrade import UpgradeStep
from opengever.workspace.workspace import FOOTER_DEFAULT_FORMAT


class InitializeFooterMeetingTemplateSettings(UpgradeStep):
    """Initialize footer meeting template settings.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'opengever.workspace.workspace'}
        for workspace in self.objects(query, "Initalize footer meeting template settings"):
            if not workspace.meeting_template_footer:
                workspace.meeting_template_footer = FOOTER_DEFAULT_FORMAT
