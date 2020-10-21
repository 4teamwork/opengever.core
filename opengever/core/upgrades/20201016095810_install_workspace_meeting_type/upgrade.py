from ftw.upgrade import UpgradeStep


class InstallWorkspaceMeetingType(UpgradeStep):
    """Install WorkspaceMeeting type.
    """

    def __call__(self):
        self.install_upgrade_profile()
