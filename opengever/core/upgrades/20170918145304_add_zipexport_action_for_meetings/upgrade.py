from ftw.upgrade import UpgradeStep


class AddZipexportActionForMeetings(UpgradeStep):
    """Add zipexport action for meetings.
    """

    def __call__(self):
        self.install_upgrade_profile()
