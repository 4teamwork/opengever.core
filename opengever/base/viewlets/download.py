from opengever.base import _
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.document.versioner import Versioner
from plone.dexterity.primary import PrimaryFieldInfo
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class DownloadFileVersion(BrowserView):
    """Download a specific version of an opengever document."""

    def _init_version_file(self):
        version_id = self.request.get('version_id')

        old_obj = Versioner(self.context).retrieve(version_id)
        primary_field_info = PrimaryFieldInfo(old_obj)
        self.version_file = primary_field_info.value

    def render(self):
        self._init_version_file()
        if not self.version_file:
            msg = _(u'No file in in this version')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader('Content-Type', self.version_file.contentType)
        response.setHeader('Content-Length', self.version_file.getSize())
        set_attachment_content_disposition(
            self.request, self.version_file.filename.encode('utf-8'))

        return self.version_file.data
