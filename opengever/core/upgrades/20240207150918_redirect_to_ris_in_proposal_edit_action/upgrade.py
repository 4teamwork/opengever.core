from ftw.upgrade import UpgradeStep


class RedirectToRisInProposalEditAction(UpgradeStep):
    """Redirect to ris in proposal edit action.
    """

    def __call__(self):
        self.install_upgrade_profile()
