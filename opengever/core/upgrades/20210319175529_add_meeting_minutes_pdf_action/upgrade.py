from ftw.upgrade import UpgradeStep


class AddMeetingMinutesPDFAction(UpgradeStep):
    """Add meeting minutes pdf action.
    """

    def __call__(self):
        self.install_upgrade_profile()
