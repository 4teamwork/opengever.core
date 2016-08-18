from ftw.upgrade import UpgradeStep


class FixShowroomCSSOrder(UpgradeStep):
    """Fix showroom css order.
    """

    def __call__(self):
        self.install_upgrade_profile()
