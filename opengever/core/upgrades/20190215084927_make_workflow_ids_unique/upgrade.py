from ftw.upgrade import UpgradeStep


class MakeWorkflowIdsUnique(UpgradeStep):
    """Make workflow ids unique.
    """

    def __call__(self):
        self.install_upgrade_profile()
