from ftw.upgrade import UpgradeStep


class AddProposalTemplateFTI(UpgradeStep):
    """Add proposal template FTI.
    """

    def __call__(self):
        self.install_upgrade_profile()
