from ftw.upgrade import UpgradeStep


class ConfigureTabbedviewAsDefaultViewForWorkspace(UpgradeStep):
    """Configure tabbedview as default view for workspace.
    """

    def __call__(self):
        self.install_upgrade_profile()
