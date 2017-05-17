from ftw.upgrade import UpgradeStep


class RemoveCreatorFromMeetings(UpgradeStep):
    """Remove creator from meetings.
    """

    def __call__(self):
        self.install_upgrade_profile()
