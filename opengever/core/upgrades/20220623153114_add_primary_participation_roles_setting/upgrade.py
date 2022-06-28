from ftw.upgrade import UpgradeStep


class AddPrimaryParticipationRolesSetting(UpgradeStep):
    """Add primary participation roles setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
