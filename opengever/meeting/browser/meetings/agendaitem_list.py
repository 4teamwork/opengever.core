from opengever.meeting import _
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.sablon import Sablon
from plone import api
from Products.Five.browser import BrowserView


class DownloadAgendaItemList(BrowserView):

    operations = AgendaItemListOperations()

    def __init__(self, context, request):
        super(DownloadAgendaItemList, self).__init__(context, request)
        self.model = context.model

    def get_json_data(self, pretty=False):
        return self.operations.get_meeting_data(
            self.model).as_json(pretty=pretty)

    def __call__(self):
        template = self.operations.get_sablon_template(self.model)
        if not template:
            api.portal.show_message(
                _('msg_no_agenaitem_list_template',
                  default=u'There is no agendaitem list template configured, '
                  'agendaitem list could not be generated.'),
                request=self.request,
                type='error')

            return self.request.RESPONSE.redirect(self.model.get_url())

        sablon = Sablon(template)
        sablon.process(self.get_json_data())

        assert sablon.is_processed_successfully(), sablon.stderr
        filename = self.operations.get_filename(self.model).encode('utf-8')
        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', MIME_DOCX)
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format(filename))
        return sablon.file_data

    def as_json(self):
        """Returns the protocol data as json
        """
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        return self.get_json_data(pretty=True)
