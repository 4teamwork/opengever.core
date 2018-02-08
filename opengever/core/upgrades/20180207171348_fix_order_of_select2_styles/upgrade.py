from ftw.upgrade import UpgradeStep


class FixOrderOfSelect2Styles(UpgradeStep):
    """Fix order of select2 styles.
    """

    def __call__(self):
        self.install_upgrade_profile()
