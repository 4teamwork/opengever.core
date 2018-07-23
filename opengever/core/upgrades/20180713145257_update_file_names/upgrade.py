from ftw.upgrade import UpgradeStep
from opengever.document.subscribers import sync_title_and_filename_handler


class UpdateFileNames(UpgradeStep):
    """Update file names for documents and E-mails
    """

    def __call__(self):
        # Sync document filenames with title
        for obj in self.objects({'portal_type': 'opengever.document.document'},
                                'Synchronize document filenames with title'):
            sync_title_and_filename_handler(obj, None)

        # Sync E-mail filenames with title
        for obj in self.objects({'portal_type': 'ftw.mail.mail'},
                                'Synchronize E-mail filenames with title'):
            obj.update_filename()
