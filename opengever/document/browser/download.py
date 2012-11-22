from five import grok
from opengever.base.viewlets.download import DownloadFileVersion
from opengever.document.document import IDocumentSchema
from opengever.document.events import FileCopyDownloadedEvent
from plone.namedfile.browser import Download
from zope.event import notify

class DocumentDownload(Download):
    """Overriding the Namefile Download view,
    for implement the special file handling
    """

    def __call__(self):
        stream = super(DocumentDownload, self).__call__()
        notify(FileCopyDownloadedEvent(self.context))
        return stream


class DownloadConfirmation(grok.View):
    """Download Confirmation View, allways displayed in a overlay."""

    grok.context(IDocumentSchema)
    grok.name('file_download_confirmation')
    grok.require('zope2.View')


    def download_url(self):
        if self.request.get('version_id'):
            return '%s/download_file_version?version_id=%s' %(
                self.context.absolute_url(),
                self.request.get('version_id'))
        else:
            return '%s/download' %(self.context.absolute_url())


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
