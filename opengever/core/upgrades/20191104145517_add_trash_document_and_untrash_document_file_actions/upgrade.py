from ftw.upgrade import UpgradeStep


class AddTrashDocumentAndUntrashDocumentFileActions(UpgradeStep):
    """Add trash_document and untrash_document file actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
