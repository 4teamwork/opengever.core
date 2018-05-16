from ftw.upgrade import UpgradeStep


class Upgrades(UpgradeStep):
    """Upgrades to 2003.

    Disable authoring.css
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-plonetheme.teamraum.upgrades.default:2003')
