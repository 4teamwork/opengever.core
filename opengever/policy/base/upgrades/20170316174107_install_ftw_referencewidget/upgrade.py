from ftw.upgrade import UpgradeStep


class InstallFtwReferncewidget(UpgradeStep):
    """Install ftw.referncewidget.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.referencewidget:default')
        self.install_upgrade_profile()
