from zope.interface import implements
from ZPublisher.Iterators import IStreamIterator


class TempfileStreamIterator(object):

    implements(IStreamIterator)

    def __init__(self, tmpfile, size, chunksize=1 << 16):
        self.size = size
        tmpfile.seek(0)
        self.file = tmpfile
        self.chunksize = chunksize

    def __iter__(self):
        self.file.seek(0)
        return self

    def next(self):
        data = self.file.read(self.chunksize)
        if not data:
            self.file.close()
            raise StopIteration
        return data

    def __len__(self):
        return self.size
