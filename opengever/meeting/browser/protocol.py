from opengever.meeting import _
from opengever.meeting.exceptions import SablonProcessingFailed
from plone import api
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

        try:
            command = meeting.update_protocol_document(
                overwrite=self.request.get("overwrite") == "True")
            command.show_message()
        except SablonProcessingFailed:
            msg = _(u'Error while processing Sablon template')
            api.portal.show_message(msg, self.request, type='error')

        return self.request.RESPONSE.redirect(meeting.get_url())
