from ftw.upgrade import UpgradeStep


class AddARegistrySettingForOneoffixxBaseurl(UpgradeStep):
    """Add a registry setting for Oneoffixx baseurl.
    """

    def __call__(self):
        self.install_upgrade_profile()
