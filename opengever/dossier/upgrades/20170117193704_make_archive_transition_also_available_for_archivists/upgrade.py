from ftw.upgrade import UpgradeStep


class MakeArchiveTransitionAlsoAvailableForArchivists(UpgradeStep):
    """Make archive transition also available for archivists.
    """

    def __call__(self):
        self.install_upgrade_profile()
