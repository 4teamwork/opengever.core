from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView


class MergeDocxProtocol(BrowserView):
    """Create a protocol merged from several partial protocols."""

    operations = ProtocolOperations()

    @classmethod
    def url_for(cls, meeting, overwrite=False):
        dossier = meeting.get_dossier()

        url = '{}/@@merge_docx_protocol?meeting-id={}&overwrite={}'.format(
            dossier.absolute_url(), meeting.meeting_id, overwrite)
        return addTokenToUrl(url)

    def __call__(self):
        meeting = self.context.get_meeting()
        command = MergeDocxProtocolCommand(
            self.context, meeting, self.operations)
        overwrite = self.request.get("overwrite") == "True"
        command.execute(overwrite)
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())
