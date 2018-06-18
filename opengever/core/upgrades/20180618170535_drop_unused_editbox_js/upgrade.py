from ftw.upgrade import UpgradeStep


class DropUnusedEditboxJs(UpgradeStep):
    """Drop unused Editbox.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
