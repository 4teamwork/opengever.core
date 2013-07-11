from ftw.upgrade import UpgradeStep


class InstallTeamraumTheme(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.contentmenu:default')
        self.setup_install_profile(
            'profile-collective.mtrsetup:default')
        self.setup_install_profile(
            'profile-plonetheme.teamraum:gever')
        self.setup_install_profile(
            'profile-opengever.examplecontent.upgrades:2501')
