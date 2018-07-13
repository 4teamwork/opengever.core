from ftw.upgrade import UpgradeStep


class MeetingTemplates(UpgradeStep):
    """Meeting Templates.
    """

    def __call__(self):
        self.install_upgrade_profile()
