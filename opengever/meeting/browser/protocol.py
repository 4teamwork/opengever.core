from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView


class MergeDocxProtocol(BrowserView):
    """Create a protocol merged from several partial protocols."""

    operations = ProtocolOperations()

    @classmethod
    def url_for(cls, meeting):
        dossier = meeting.get_dossier()

        url = '{}/@@merge_docx_protocol?meeting-id={}'.format(
            dossier.absolute_url(), meeting.meeting_id)
        return addTokenToUrl(url)

    def __call__(self):
        meeting = self.context.get_meeting()
        command = MergeDocxProtocolCommand(
            self.context, meeting, self.operations)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())
