from opengever.disposition.ech0160.model.folder import Folder
import os.path


class ContentRootFolder(Folder):
    """eCH-0160 content root folder of type ordnerSIP"""

    def __init__(self, base_path):
        self.next_folder = 1
        self.next_file = 1
        self.name = u'content'
        self.path = os.path.join(base_path, self.name)
        self.folders = []
        self.files = []

    def increment_folder_counter(self):
        self.next_folder += 1

    def add_dossier(self, dossier):
        self.folders.append(Folder(self, dossier, self.path))
