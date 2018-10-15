from ftw.upgrade import UpgradeStep


class MakeOneoffixxTextlineConfigsOptionalSoTheyCanBeUnset(UpgradeStep):
    """Make Oneoffixx textline configs optional so they can be unset.
    """

    def __call__(self):
        self.install_upgrade_profile()
