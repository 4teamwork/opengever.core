from plone.namedfile.interfaces import IStorage
from plone.namedfile.interfaces import NotStorable
from zope.interface import implementer
from ZPublisher.HTTPRequest import FileUpload

MAXCHUNKSIZE = 1 << 16


# IStorage utility for good old ZPublisher.HTTPRequest.FileUpload
# Would make sense to have this in plone.namedfile
@implementer(IStorage)
class FileUploadStorable(object):

    def store(self, data, blob):
        if not isinstance(data, FileUpload):
            raise NotStorable('Could not store data (not of "FileUpload").')

        data.seek(0)

        fp = blob.open('w')
        block = data.read(MAXCHUNKSIZE)
        while block:
            fp.write(block)
            block = data.read(MAXCHUNKSIZE)
        fp.close()
