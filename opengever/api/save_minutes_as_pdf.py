from opengever.api import _
from opengever.base.command import CreateDocumentCommand
from opengever.workspace.browser.meeting_pdf import MeetingMinutesPDFView
from opengever.workspace.interfaces import IWorkspaceMeeting
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.i18n import translate
from zope.interface import alsoProvides


class SaveMinutesAsPDFPost(Service):

    def get_meeting(self, data):
        uid = data.get('meeting_uid', None)
        if not uid:
            return
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=uid, object_provides=[IWorkspaceMeeting.__identifier__])
        if brains:
            return brains[0].getObject()

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)
        meeting = self.get_meeting(data)
        if not meeting:
            raise BadRequest(
                "Property 'meeting_uid' is required and should be a UID of a WorkspaceMeeting")

        # Get minutes PDF for meeting
        minutes_data = MeetingMinutesPDFView(meeting, self.request)()

        minutes_title = translate(_(
            u'label_workspace_meeting_minutes',
            default=u'Minutes for ${meeting_title}',
            mapping={'meeting_title': meeting.title}
        ), context=self.request)

        filename = "minutes.pdf"
        command = CreateDocumentCommand(self.context, filename, minutes_data,
                                        title=minutes_title)
        destination_document = command.execute()

        self.request.response.setHeader("Location", destination_document.absolute_url())
        self.reply_no_content(201)
