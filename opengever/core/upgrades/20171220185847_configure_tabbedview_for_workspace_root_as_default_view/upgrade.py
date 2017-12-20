from ftw.upgrade import UpgradeStep


class ConfigureTabbedviewForWorkspaceRootAsDefaultView(UpgradeStep):
    """Configure tabbedview for workspace root as default view.
    """

    def __call__(self):
        self.install_upgrade_profile()
