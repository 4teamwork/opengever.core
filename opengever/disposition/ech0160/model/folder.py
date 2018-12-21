from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.model import File
import os.path


class Folder(object):
    """eCH-0160 ordnerSIP"""

    def __init__(self, toc, dossier, base_path):
        self.folders = []
        self.files = []

        self.name = u'd{0:06d}'.format(toc.next_folder)
        toc.increment_folder_counter()
        self.path = os.path.join(base_path, self.name)

        for subdossier in dossier.dossiers.values():
            self.folders.append(Folder(toc, subdossier, self.path))

        for doc in dossier.documents.values():
            if doc.obj.archival_file or doc.obj.file:
                self.files.append(File(toc, doc))

    def binding(self):
        ordner = arelda.ordnerSIP(self.name)

        for folder in self.folders:
            ordner.ordner.append(folder.binding())

        for file_ in self.files:
            ordner.datei.append(file_.binding())

        return ordner

    def add_to_zip(self, zipfile):
        for file_ in self.files:
            zipfile.write(file_.filepath, os.path.join(self.path, file_.name))
        for folder in self.folders:
            folder.add_to_zip(zipfile)
