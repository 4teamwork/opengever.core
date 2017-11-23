from ftw.upgrade import UpgradeStep


class AddOnenoteMimetype(UpgradeStep):
    """Add onenote mimetype.
    """

    def __call__(self):
        self.install_upgrade_profile()
