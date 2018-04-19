from ftw.upgrade import UpgradeStep


class RegisterVueAndAxiosJS(UpgradeStep):
    """Register vue and axios JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
