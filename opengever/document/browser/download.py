from five import grok
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.viewlets.download import DownloadFileVersion
from opengever.document.document import IDocumentSchema
from opengever.document.events import FileCopyDownloadedEvent
from plone.namedfile.browser import Download
from plone.namedfile.utils import stream_data
from zope.event import notify


class DocumentishDownload(Download):
    """Overriding the Namefile Download view and implement some OpenGever
    specific file handling:

    - Deal with an unicode bug in plone.namedfile.utils.set_header
    - Set Content-Disposition headers based on browser sniffing
    - Fire our own `FileCopyDownloadedEvent`
    """

    def __call__(self):

        named_file = self._getFile()
        if not self.filename:
            self.filename = getattr(named_file, 'filename', self.fieldname)

        if self.filename:
            self.filename = self.filename.encode('utf-8')

        set_attachment_content_disposition(self.request, self.filename,
                                           named_file)
        notify(FileCopyDownloadedEvent(self.context))

        return self.stream_data(named_file)

    def stream_data(self, named_file):
        return stream_data(named_file)


class DownloadConfirmation(grok.View):
    """Download Confirmation View, allways displayed in a overlay.
    """

    grok.context(IDocumentSchema)
    grok.name('file_download_confirmation')
    grok.require('zope2.View')

    def download_url(self):
        if self.request.get('version_id'):
            return '%s/download_file_version?version_id=%s' % (
                self.context.absolute_url(),
                self.request.get('version_id'))
        else:
            return '%s/download' % (self.context.absolute_url())


class DocumentDownloadFileVersion(DownloadFileVersion):
    """The default GEVER download file version view,
    but includes notifying FileCopyDownloadedEvent used for journalizing.
    """

    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.name('download_file_version')

    def render(self):
        self._init_version_file()
        if self.version_file:
            notify(FileCopyDownloadedEvent(self.context))
        return super(DocumentDownloadFileVersion, self).render()
