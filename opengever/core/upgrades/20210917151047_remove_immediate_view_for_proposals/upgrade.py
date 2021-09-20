from ftw.upgrade import UpgradeStep


class RemoveImmediateViewForProposals(UpgradeStep):
    """Remove immediate view for proposals.
    """

    def __call__(self):
        self.install_upgrade_profile()
