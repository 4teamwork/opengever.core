from ftw.upgrade import UpgradeStep


class AddClassificationVocabularies(UpgradeStep):
    """Add classification vocabularies.
    """

    def __call__(self):
        self.install_upgrade_profile()
