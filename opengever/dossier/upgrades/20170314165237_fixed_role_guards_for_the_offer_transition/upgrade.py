from ftw.upgrade import UpgradeStep


class FixedRoleGuardsForTheOfferTransition(UpgradeStep):
    """Fixed role guards for the offer transition.
    """

    def __call__(self):
        self.install_upgrade_profile()
