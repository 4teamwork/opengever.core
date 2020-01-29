from ftw.upgrade import UpgradeStep


class AddMoveProposalItemsAction(UpgradeStep):
    """Add move proposal items action.
    """

    def __call__(self):
        self.install_upgrade_profile()
