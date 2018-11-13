from ftw.upgrade import UpgradeStep


class AddOpenXMLVisioToMimetypeRegistry(UpgradeStep):
    """Add Open XML Visio to mimetype registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
