from ftw.upgrade import UpgradeStep


class SwitchSubmittedProposalSchema(UpgradeStep):
    """Switch submitted proposal schema.
    """

    def __call__(self):
        self.install_upgrade_profile()
