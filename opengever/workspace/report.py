from opengever.globalindex.browser.report import UserReport
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.workspace')


class WorkspaceParticipantsReport(UserReport):
    """View that generate an excel spreadsheet which list all selected users
    """

    @property
    def filename(self):
        participants = translate(_("Participants"), context=self.request)
        return "{participants}_{workspace_title}.xlsx".format(
            participants=participants,
            workspace_title=self.context.title
        )

    def check_permissions(self):
        pass
