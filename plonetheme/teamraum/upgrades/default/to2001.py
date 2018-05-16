from ftw.upgrade import UpgradeStep


class UpgradeViewlets(UpgradeStep):
    """Upgrade viewlets
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-plonetheme.teamraum.upgrades.default:2001')
