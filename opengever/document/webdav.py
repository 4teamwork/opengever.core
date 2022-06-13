"""
Webdav support for Document
"""
from opengever.document.document import IDocumentSchema
from opengever.document.versioner import Versioner
from plone.dexterity import filerepresentation
from plone.memoize.instance import memoize
from StringIO import StringIO
import tempfile


class DocumentReadFile(filerepresentation.DefaultReadFile):

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
        raise NotImplementedError

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


class DocumentWriteFile(filerepresentation.DefaultWriteFile):

    @property
    def filefield(self):
        return IDocumentSchema.get('file').get(self.context)

    @property
    def mimeType(self):
        return self.filefield.contentType

    @mimeType.setter
    def mimeType(self, value):
        self.filefield.contentType = value

    @property
    def encoding(self):
        return 'utf8'

    @property
    def name(self):
        return self.filefield.filename

    @name.setter
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
        versioner = Versioner(self.context)
        if not versioner.has_initial_version():
            versioner.create_initial_version()

        self.filefield.data = self.stream.read()
