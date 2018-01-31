from ftw.upgrade import UpgradeStep


class AddMyInvitationAction(UpgradeStep):
    """Add my invitation action.
    """

    def __call__(self):
        self.install_upgrade_profile()
