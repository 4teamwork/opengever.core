from ftw.upgrade import UpgradeStep


class RegisterEditorJavascript(UpgradeStep):
    """Register editor javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
