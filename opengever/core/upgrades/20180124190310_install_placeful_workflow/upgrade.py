from ftw.upgrade import UpgradeStep


class InstallPlacefulWorkflow(UpgradeStep):
    """Install placeful workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
