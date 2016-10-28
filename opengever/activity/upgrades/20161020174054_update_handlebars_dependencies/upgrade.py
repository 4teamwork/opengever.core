from ftw.upgrade import UpgradeStep


class UpdateHandlebarsDependencies(UpgradeStep):
    """Update handlebars dependencies.
    """

    def __call__(self):
        self.install_upgrade_profile()
