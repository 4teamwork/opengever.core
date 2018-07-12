from ftw.upgrade import UpgradeStep


class UninstallWebcomponentsBundleFromJavascriptLibrary(UpgradeStep):
    """Uninstall webcomponents bundle from javascript library.
    """

    def __call__(self):
        self.install_upgrade_profile()
