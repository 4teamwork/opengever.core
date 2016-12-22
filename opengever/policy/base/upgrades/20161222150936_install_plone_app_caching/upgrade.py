from ftw.upgrade import UpgradeStep


class InstallPloneAppCaching(UpgradeStep):
    """Install plone.app.caching.
    """

    def __call__(self):
        self.setup_install_profile('profile-plone.app.caching:default')
        self.setup_install_profile('profile-plone.app.caching:without-caching-proxy')
        self.install_upgrade_profile()
