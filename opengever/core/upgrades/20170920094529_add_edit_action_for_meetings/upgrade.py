from ftw.upgrade import UpgradeStep


class AddEditActionForMeetings(UpgradeStep):
    """Add edit action for meetings.
    """

    def __call__(self):
        self.install_upgrade_profile()
