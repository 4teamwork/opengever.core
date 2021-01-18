from ftw.upgrade import UpgradeStep


class EnableCustomPropertiesForDocumentsMails(UpgradeStep):
    """Enable custom properties for documents/mails.
    """

    def __call__(self):
        self.install_upgrade_profile()
