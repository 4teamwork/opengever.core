from ftw.upgrade import UpgradeStep


class AddConfirmationToCancelCheckout(UpgradeStep):
    """Add confirmation to cancel checkout.
    """

    def __call__(self):
        self.install_upgrade_profile()
