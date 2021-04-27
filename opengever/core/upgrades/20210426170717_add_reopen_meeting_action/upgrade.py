from ftw.upgrade import UpgradeStep


class AddReopenMeetingAction(UpgradeStep):
    """Add reopen meeting action.
    """

    def __call__(self):
        self.install_upgrade_profile()
