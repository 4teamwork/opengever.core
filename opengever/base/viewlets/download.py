from opengever.base import _
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.document.versioner import Versioner
from plone.dexterity.primary import PrimaryFieldInfo
from plone.namedfile.utils import stream_data
from Products.CMFEditions.interfaces.IArchivist import ArchivistRetrieveError
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest


class DownloadFileVersion(BrowserView):
    """Download a specific version of an opengever document."""

    def _init_version_file(self):
        version_id = self.request.get('version_id')
        if version_id is None:
            raise BadRequest(u'Missing parameter "version_id".')
        try:
            version_id = int(version_id)
        except ValueError:
            raise BadRequest(u'Invalid version id "{}".'.format(version_id))

        versioner = Versioner(self.context)
        if not versioner.has_initial_version() and version_id == 0:
            obj = self.context
        else:
            try:
                obj = versioner.retrieve(version_id)
            except ArchivistRetrieveError:
                raise BadRequest(
                    u'Version "{}" does not exist.'.format(version_id)
                )

        primary_field_info = PrimaryFieldInfo(obj)
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

        return stream_data(self.version_file)
