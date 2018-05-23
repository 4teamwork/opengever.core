from ftw.upgrade import UpgradeStep


class Upgrades(UpgradeStep):
    """Upgrades to 2002.

    Include ftw.mobilenavigation
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.mobilenavigation:default')
        self.setup_install_profile(
            'profile-plonetheme.teamraum.upgrades.default:2002')
