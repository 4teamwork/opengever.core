from ftw.upgrade import UpgradeStep


class AddTasksAsZipExportables(UpgradeStep):
    """Add tasks as zip exportables.
    """

    def __call__(self):
        self.install_upgrade_profile()
