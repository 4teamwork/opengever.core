"""
Webdav support for Document
"""

from five import grok
from opengever.document.document import IDocumentSchema
from plone.dexterity import filerepresentation
from plone.memoize.instance import memoize
from rwproperty import getproperty, setproperty
from StringIO import StringIO
from zope.filerepresentation.interfaces import IRawReadFile, IRawWriteFile
import tempfile


class DocumentReadFile(filerepresentation.DefaultReadFile, grok.Adapter):
    grok.implements(IRawReadFile)
    grok.provides(IRawReadFile)
    grok.context(IDocumentSchema)

    @property
    def filefield(self):
        return IDocumentSchema.get('file').get(self.context)

    @memoize
    def _getStream(self):
        """Construct message on demand
        """
        streaming_supported = False
        try:
            self.filefield.open
            streaming_supported = True
        except AttributeError:
            pass
        if streaming_supported:

            # TODO: XXX
            # copy Document.data in to a temporary file, so we can avoid the
            # the error:
            #    BlobError: Already opened for reading.
            tmp = tempfile.TemporaryFile(mode='w+b')
            tmp.write(self.filefield.data)
            tmp.flush()
            tmp.seek(0)
            return tmp
        else:
            return StringIO(self.filefield.data)

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
        return self.filefield.getSize()


class DocumentWriteFile(filerepresentation.DefaultWriteFile, grok.Adapter):
    grok.implements(IRawWriteFile)
    grok.context(IDocumentSchema)

    @property
    def filefield(self):
        return IDocumentSchema.get('file').get(self.context)

    @getproperty
    def mimeType(self):
        return self.filefield.contentType

    @setproperty
    def mimeType(self, value):
        self.filefield.contentType = value

    @getproperty
    def encoding(self):
        return 'utf8'

    @getproperty
    def name(self):
        return self.filefield.filename

    @setproperty
    def name(self, value):
        self.filefield.filename = value

    @property
    def stream(self):
        if '_stream' not in dir(self):
            self._stream = StringIO()
        return self._stream

    def write(self, data):
        self.stream.write(data)

    def close(self):
        self.stream.seek(0)
        self.filefield.data = self.stream.read()
