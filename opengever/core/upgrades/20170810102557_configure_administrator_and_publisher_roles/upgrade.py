from ftw.upgrade import UpgradeStep


class ConfigureAdministratorAndPublisherRoles(UpgradeStep):
    """Register Administrator- and Publisher-roles with lawgiver.
    """

    def __call__(self):
        self.install_upgrade_profile()
