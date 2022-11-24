from ftw.upgrade import UpgradeStep


class AddNewAccessHiddenMembersPermission(UpgradeStep):
    """Add new AccessHiddenMembers permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
