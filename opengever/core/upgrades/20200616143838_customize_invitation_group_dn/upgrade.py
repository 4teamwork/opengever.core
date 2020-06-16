from ftw.upgrade import UpgradeStep


class CustomizeInvitationGroupDN(UpgradeStep):
    """Customize invitation group dn.
    """

    def __call__(self):
        self.install_upgrade_profile()
