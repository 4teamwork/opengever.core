from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep


class UpgradeMailMessageFilename(UpgradeStep):

    def __call__(self):
        objects = self.catalog_unrestricted_search(
            {'portal_type': 'ftw.mail.mail'}, full_objects=True)

        for mail in ProgressLogger('Migrate mail message filename', objects):
            mail.update_filename()
