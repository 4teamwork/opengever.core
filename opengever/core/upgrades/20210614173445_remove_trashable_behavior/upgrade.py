from ftw.upgrade import UpgradeStep


class RemoveTrashableBehavior(UpgradeStep):
    """Remove trashable behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
