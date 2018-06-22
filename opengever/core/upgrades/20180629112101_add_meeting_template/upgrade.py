from ftw.upgrade import UpgradeStep


class AddMeetingTemplate(UpgradeStep):
    """Add meeting template.
    """

    def __call__(self):
        self.install_upgrade_profile()
