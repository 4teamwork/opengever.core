from plone.namedfile.interfaces import IStorage
from plone.namedfile.interfaces import NotStorable
from tempfile import _TemporaryFileWrapper
from zope.interface import implementer
from ZPublisher.HTTPRequest import FileUpload


MAXCHUNKSIZE = 1 << 16


def _chunked_transfer(data, blob):
        data.seek(0)

        fp = blob.open('w')
        block = data.read(MAXCHUNKSIZE)
        while block:
            fp.write(block)
            block = data.read(MAXCHUNKSIZE)
        fp.close()


# IStorage utility for good old ZPublisher.HTTPRequest.FileUpload
# Would make sense to have this in plone.namedfile
@implementer(IStorage)
class FileUploadStorable(object):

    def store(self, data, blob):
        if not isinstance(data, FileUpload):
            raise NotStorable('Could not store data (not of "FileUpload").')

        _chunked_transfer(data, blob)


@implementer(IStorage)
class TemporaryFileWrapperStorable(object):

    def store(self, data, blob):
        if not isinstance(data, _TemporaryFileWrapper):
            raise NotStorable('Could not store data (not a '
                              '"_TemporaryFileWrapper").')

        _chunked_transfer(data, blob)
