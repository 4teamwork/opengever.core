from ftw.upgrade import UpgradeStep


class UpdateFilenameOfMailsWithFileExtensionMsg(UpgradeStep):
    """Update filename of mails with file extension msg.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'portal_type': 'ftw.mail.mail', 'file_extension': '.msg'}
        for mail in self.objects(query, 'Update filename'):
            mail.update_filename()
            mail.reindexObject(idxs=['UID', 'filename'])
