from ftw.upgrade import UpgradeStep


class RegisterMissingDropdownJS(UpgradeStep):
    """Register missing dropdown JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
