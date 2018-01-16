from ftw.upgrade import UpgradeStep


class AddConfigurationOptionForTasksTabOnRepositoryFolder(UpgradeStep):
    """Add configuration option for tasks tab on repository folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
