from opengever.base.utils import file_checksum
from opengever.disposition.ech0160.bindings import arelda
import binascii
import os.path


class File(object):
    """eCH-0160 dateiSIP"""

    def __init__(self, toc, document, file):
        self.file = file
        self.id = u'_{}'.format(binascii.hexlify(self.file._p_oid))
        document.file_refs.append(self.id)
        document.files.append(self)
        self.document = document
        self.filename = self.file.filename

        base, extension = os.path.splitext(self.filename)
        self.name = 'p{0:06d}{1}'.format(toc.next_file, extension)
        toc.next_file += 1

    def committed_file_path(self):
        return self.file._blob.committed()

    def binding(self):
        datei = arelda.dateiSIP(id=self.id)
        datei.name = self.name
        datei.originalName = self.filename
        datei.pruefalgorithmus, datei.pruefsumme = file_checksum(self.committed_file_path())
        return datei
