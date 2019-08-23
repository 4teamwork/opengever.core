from opengever.disposition.ech0160.bindings import arelda
from opengever.base.utils import file_checksum
import binascii
import os.path


class File(object):
    """eCH-0160 dateiSIP"""

    def __init__(self, toc, document, file):
        self.file = file
        self.id = u'_{}'.format(binascii.hexlify(self.file._p_oid))
        document.file_refs.append(self.id)
        self.document = document
        self.filename = self.file.filename
        self.filepath = self.file._blob.committed()

        base, extension = os.path.splitext(self.filename)
        self.name = 'p{0:06d}{1}'.format(toc.next_file, extension)
        toc.next_file += 1

    def binding(self):
        datei = arelda.dateiSIP(id=self.id)
        datei.name = self.name
        datei.originalName = self.filename
        datei.pruefalgorithmus, datei.pruefsumme = file_checksum(self.filepath)
        return datei
