from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView


class MergeDocxProtocol(BrowserView):
    """Create a protocol merged from several partial protocols."""

    @classmethod
    def url_for(cls, meeting, overwrite=False):
        dossier = meeting.get_dossier()

        url = '{}/@@merge_docx_protocol?meeting-id={}&overwrite={}'.format(
            dossier.absolute_url(), meeting.meeting_id, overwrite)
        return addTokenToUrl(url)

    def __call__(self):
        meeting = self.context.get_meeting()

        command = meeting.update_protocol_document(
            overwrite=self.request.get("overwrite") == "True")
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())
