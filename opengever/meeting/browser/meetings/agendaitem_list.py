from opengever.meeting import _
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import UpdateGeneratedDocumentCommand
from opengever.meeting.exceptions import AgendaItemListAlreadyGenerated
from opengever.meeting.exceptions import AgendaItemListMissingTemplate
from opengever.meeting.exceptions import SablonProcessingFailed
from opengever.meeting.model import Meeting
from opengever.meeting.model.generateddocument import GeneratedAgendaItemList
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView
from zExceptions import NotFound


class GenerateAgendaItemList(BrowserView):
    """Generate an agenda item list.

    1. Generate a Word BLOB via sablon
    2. Create a new document in the meeting dossier from the BLOB
    3. Redirect back to the meeting
    """

    operations = AgendaItemListOperations()

    def __call__(self):
        meeting = self.get_meeting()

        command = CreateGeneratedDocumentCommand(
            self.context,
            meeting,
            self.operations,
            )

        try:
            command.execute()
            command.show_message()

        except AgendaItemListMissingTemplate:
            msg = _(
                u'msg_error_agendaitem_list_missing_template',
                default=(u'There is no agendaitem list template configured, agendaitem list could not be generated.'),
                mapping=dict(title=meeting.get_title()),
                )
            api.portal.show_message(msg, self.request, type='error')

        except AgendaItemListAlreadyGenerated:
            msg = _(
                u'msg_error_agendaitem_list_already_generated',
                default=(u'The agenda item list for meeting ${title} has already been generated.'),
                mapping=dict(title=meeting.get_title()),
                )
            api.portal.show_message(msg, self.request, type='error')

        except SablonProcessingFailed:
            msg = _(u'Error while processing Sablon template')
            api.portal.show_message(msg, self.request, type='error')

        return self.request.RESPONSE.redirect(meeting.get_url())

    @classmethod
    def url_for(cls, meeting):
        dossier = meeting.get_dossier()
        url = '{}/@@generate_agendaitem_list?meeting-id={}'.format(
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


class UpdateAgendaItemList(BrowserView):
    """Generate a new agenda item list version.

    1. Generate a Word BLOB via sablon
    2. Update the generated document in the meeting dossier with the BLOB
    3. Redirect back to the meeting
    """

    operations = AgendaItemListOperations()

    def __call__(self):
        meeting = self.get_meeting()
        generated_doc = self.get_generated_document()

        command = UpdateGeneratedDocumentCommand(
            generated_doc, meeting, self.operations)

        try:
            command.execute()
            command.show_message()

        except SablonProcessingFailed:
            msg = _(u'Error while processing Sablon template')
            api.portal.show_message(msg, self.request, type='error')

        return self.request.RESPONSE.redirect(meeting.get_url())

    @classmethod
    def url_for(cls, meeting):
        generated_document = meeting.agendaitem_list_document
        document = generated_document.resolve_document()
        url = '{}/@@update_agendaitem_list?document-id={}&meeting-id={}'.format(
            document.absolute_url(),
            generated_document.document_id,
            meeting.meeting_id)
        return addTokenToUrl(url)

    def get_generated_document(self):
        document_id = self.request.get('document-id')
        if not document_id:
            raise NotFound

        document = GeneratedAgendaItemList.get(document_id)
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


class DownloadGeneratedAgendaItemList(BrowserView):
    """Download the generated agenda item list for a meeting."""

    operations = AgendaItemListOperations()

    def __init__(self, context, request):
        super(DownloadGeneratedAgendaItemList, self).__init__(context, request)
        self._model = context.model

    def get_json_data(self, pretty=False):
        return self.operations.get_meeting_data(
            self._model).as_json(pretty=pretty)

    def as_json(self):
        """Renders protocol data as json."""
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        return self.get_json_data(pretty=True)
