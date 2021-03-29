from ftw.upgrade import UpgradeStep


class AddWorkspaceMeetingICalExportAction(UpgradeStep):
    """Add WorkspaceMeeting ICal Export Action.
    """

    def __call__(self):
        self.install_upgrade_profile()
