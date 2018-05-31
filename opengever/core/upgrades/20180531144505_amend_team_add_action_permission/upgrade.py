from ftw.upgrade import UpgradeStep


class AmendTeamAddActionPermission(UpgradeStep):
    """Amend Team add action permission."""

    def __call__(self):
        self.install_upgrade_profile()
