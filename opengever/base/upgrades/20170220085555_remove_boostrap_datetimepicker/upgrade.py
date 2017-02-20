from ftw.upgrade import UpgradeStep


class RemoveBoostrapDatetimepicker(UpgradeStep):
    """Remove boostrap datetimepicker.
    """

    def __call__(self):
        self.install_upgrade_profile()
