from ftw.upgrade import UpgradeStep


class AdjustSortOrderOfActions(UpgradeStep):
    """Adjust sort order of actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
