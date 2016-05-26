from ftw.upgrade import UpgradeStep


class AddCommitteeTransitionActions(UpgradeStep):
    """Add committee transition actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
