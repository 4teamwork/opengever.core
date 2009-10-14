"""
Webdav support for Document
"""

from zope.filerepresentation.interfaces import IRawReadFile

from five import grok

from plone.memoize.instance import memoize
from plone.dexterity import filerepresentation

from opengever.document.document import IDocumentSchema

class DocumentReadFile(filerepresentation.DefaultReadFile, grok.Adapter):
    grok.implements(IRawReadFile)
    grok.context(IDocumentSchema)

    def __init__(self, context):
        self.context = context
        self.filefield = IDocumentSchema.get('file').get(self.context)

    @memoize
    def _getStream(self):
        """Construct message on demand
        """
        return self.filefield.open()

    def _getMessage(self):
        raise NotImplemented

    @property
    def encoding(self):
        return 'utf8'

    @property
    def name(self):
        return self.filefield.filename

    @property
    def mimeType(self):
        return self.filefield.contentType

    def size(self):
        return self.filefield.size

