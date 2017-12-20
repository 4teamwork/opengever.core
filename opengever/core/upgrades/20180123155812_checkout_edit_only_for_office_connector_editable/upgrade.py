from ftw.upgrade import UpgradeStep


class CheckoutEditOnlyForOfficeConnectorEditable(UpgradeStep):
    """Checkout edit only for office connector editable.
    """

    def __call__(self):
        self.install_upgrade_profile()
