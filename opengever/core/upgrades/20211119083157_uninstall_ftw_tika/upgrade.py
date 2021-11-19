from ftw.upgrade import UpgradeStep


class UninstallFtwTika(UpgradeStep):
    """Uninstall ftw.tika.
    """

    def __call__(self):
        # In some cases the tika product is still installed but the profile is
        # no longer installed. This makes it hard to uninstall the product.
        # Therefore we reinstall the profile and uninstall the product
        # afterwards.
        self.setup_install_profile('ftw.tika:default')

        self.uninstall_product('ftw.tika')
