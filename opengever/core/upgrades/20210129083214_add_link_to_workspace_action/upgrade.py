from ftw.upgrade import UpgradeStep


class AddLinkToWorkspaceAction(UpgradeStep):
    """Add link_to_workspace action.
    """

    def __call__(self):
        self.install_upgrade_profile()
