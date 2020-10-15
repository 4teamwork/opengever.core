from ftw.upgrade import UpgradeStep


class AddVideoconferencingURLsToWorkspaces(UpgradeStep):
    """Add videoconferencing URLs to workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
