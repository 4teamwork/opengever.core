from five import grok
from opengever.document.document import IDocumentSchema
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.command import UpdateGeneratedDocumentCommand
from opengever.meeting.interfaces import IMeetingDossier
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import Meeting
from plone.protect.utils import addTokenToUrl
from zExceptions import NotFound


class GenerateProtocol(grok.View):
    grok.context(IMeetingDossier)
    grok.name('generate_protocol')
    grok.require('cmf.AddPortalContent')

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

        meeting = Meeting.get(meeting_id)
        if not meeting:
            raise NotFound

        return meeting

    def render(self):
        meeting = self.get_meeting()

        command = CreateGeneratedDocumentCommand(
            self.context, meeting, self.operations,
            lock_document_after_creation=True)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())


class UpdateProtocol(grok.View):
    grok.context(IDocumentSchema)
    grok.name('update_protocol')
    grok.require('cmf.ModifyPortalContent')

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

    def render(self):
        meeting = self.get_meeting()
        generated_doc = self.get_generated_document()

        command = UpdateGeneratedDocumentCommand(
            generated_doc, self.operations)
        command.execute()
        command.show_message()

        return self.request.RESPONSE.redirect(meeting.get_url())
