from ftw.upgrade import UpgradeStep


class AddContactJS(UpgradeStep):
    """Add contact js.
    """

    def __call__(self):
        self.install_upgrade_profile()
