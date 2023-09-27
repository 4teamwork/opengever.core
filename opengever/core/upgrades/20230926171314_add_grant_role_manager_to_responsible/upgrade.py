from ftw.upgrade import UpgradeStep


class AddGrantRoleManagerToResponsible(UpgradeStep):
    """Add grant role manager to responsible feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
