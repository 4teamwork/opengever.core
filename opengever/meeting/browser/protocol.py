from opengever.meeting import _
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.command import UpdateGeneratedDocumentCommand
from opengever.meeting.exceptions import ProtocolAlreadyGenerated
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView
from zExceptions import NotFound


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
            self.context, meeting, self.operations,
            lock_document_after_creation=True)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())


class GenerateProtocol(BrowserView):

    operations = ProtocolOperations()

    @classmethod
    def url_for(cls, meeting):
        dossier = meeting.get_dossier()
        url = '{}/@@generate_protocol?meeting-id={}'.format(
            dossier.absolute_url(), meeting.meeting_id)
        return addTokenToUrl(url)

    def get_meeting(self):
        meeting_id = self.request.get('meeting-id')
        if not meeting_id:
            raise NotFound

        meeting = Meeting.query.with_for_update().get(meeting_id)
        if not meeting:
            raise NotFound

        return meeting

    def __call__(self):
        meeting = self.get_meeting()
        command = CreateGeneratedDocumentCommand(
            self.context, meeting, self.operations,
            lock_document_after_creation=True)
        try:
            command.execute()
            command.show_message()
        except ProtocolAlreadyGenerated:
            msg = _(u'msg_error_protocol_already_generated',
                    default=u'The protocol for meeting ${title} has already '
                            u'been generated.',
                    mapping=dict(title=meeting.get_title()))
            api.portal.show_message(msg, self.request, type='error')

        return self.request.RESPONSE.redirect(meeting.get_url())


class UpdateProtocol(BrowserView):

    operations = ProtocolOperations()

    @classmethod
    def url_for(cls, meeting):
        generated_document = meeting.protocol_document
        document = generated_document.resolve_document()
        return '{}/@@update_protocol?document-id={}&meeting-id={}'.format(
            document.absolute_url(),
            generated_document.document_id,
            meeting.meeting_id)

    def get_generated_document(self):
        document_id = self.request.get('document-id')
        if not document_id:
            raise NotFound

        document = GeneratedProtocol.get(document_id)
        if not document:
            raise NotFound

        return document

    def get_meeting(self):
        meeting_id = self.request.get('meeting-id')
        if not meeting_id:
            raise NotFound

        meeting = Meeting.get(meeting_id)
        if not meeting:
            raise NotFound

        return meeting

    def __call__(self):
        meeting = self.get_meeting()
        generated_doc = self.get_generated_document()

        command = UpdateGeneratedDocumentCommand(
            generated_doc, meeting, self.operations)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())
