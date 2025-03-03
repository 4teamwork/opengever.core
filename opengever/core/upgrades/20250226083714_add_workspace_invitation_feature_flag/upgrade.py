from ftw.upgrade import UpgradeStep


class AddWorkspaceInvitationFeatureFlag(UpgradeStep):
    """Add workspace invitation feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
