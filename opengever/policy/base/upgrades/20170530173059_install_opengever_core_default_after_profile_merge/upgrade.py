from ftw.upgrade import UpgradeStep


class InstallOpengeverCoreDefaultAfterProfileMerge(UpgradeStep):
    """Install opengever.core:default after profile merge.
    """

    def __call__(self):
        self.install_upgrade_profile()

        profileid = 'opengever.core:default'
        if not self.is_profile_installed(profileid):
            self.portal_setup.setLastVersionForProfile(profileid, '1')

        product = 'opengever.core'
        if not self.is_profile_installed('opengever.core'):
            quickinstaller = self.getToolByName('portal_quickinstaller')
            quickinstaller.notifyInstalled(
                product,
                installedversion=quickinstaller.getProductVersion(product),
                status='installed')
