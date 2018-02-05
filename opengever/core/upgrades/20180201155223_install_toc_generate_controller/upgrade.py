from ftw.upgrade import UpgradeStep


class InstallTOCGenerateController(UpgradeStep):
    """Install toc generate controller.
    """

    def __call__(self):
        self.install_upgrade_profile()
