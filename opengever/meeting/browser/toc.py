from opengever.meeting import _
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.sablon import Sablon
from plone import api
from Products.Five.browser import BrowserView
from opengever.meeting.toc.alphabetical import AlphabeticalToc


class DownloadAlphabeticalTOC(BrowserView):

    def __init__(self, context, request):
        super(DownloadAlphabeticalTOC, self).__init__(context, request)
        self.model = context.model

    def __call__(self):
        template = self.model.get_toc_template()
        if not template:
            api.portal.show_message(
                _('msg_no_toc_template',
                  default=u'There is no toc template configured, toc could '
                          'not be generated.'),
                request=self.request,
                type='error')

            return self.request.RESPONSE.redirect(
                "{}/#periods".format(self.context.parent.absolute_url()))

        sablon = Sablon(template)
        sablon.process(self.get_json_data())

        assert sablon.is_processed_successfully(), sablon.stderr
        filename = self.model.get_toc_filename().encode('utf-8')
        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', MIME_DOCX)
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format(filename))
        return sablon.file_data

    def get_json_data(self, pretty=False):
        return AlphabeticalToc(self.model).get_json()

