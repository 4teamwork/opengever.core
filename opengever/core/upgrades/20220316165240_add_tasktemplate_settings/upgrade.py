from ftw.upgrade import UpgradeStep


class AddTasktemplateSettings(UpgradeStep):
    """Add tasktemplate settings.
    """

    def __call__(self):
        self.install_upgrade_profile()
