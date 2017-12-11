from ftw.upgrade import UpgradeStep


class LetAdministratorsSaveNewVersions(UpgradeStep):
    """let administrators save new versions.
    """

    def __call__(self):
        self.install_upgrade_profile()
