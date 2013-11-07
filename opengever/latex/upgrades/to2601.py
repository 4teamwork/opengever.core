from ftw.upgrade import UpgradeStep


class InitalizeLaTeXSettings(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.latex.upgrades:2601')
