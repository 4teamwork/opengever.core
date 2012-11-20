from five import grok
from opengever.document.document import IDocumentSchema
from plone.namedfile.browser import Download
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.event import notify
from opengever.document.events import FileCopyDownloadedEvent


class DocumentDownload(Download):
    """Overriding the Namefile Download view,
    for implement the special file handling
    """

    def __call__(self):
        stream = super(DocumentDownload, self).__call__()
        notify(FileCopyDownloadedEvent(self.context))
        return stream
