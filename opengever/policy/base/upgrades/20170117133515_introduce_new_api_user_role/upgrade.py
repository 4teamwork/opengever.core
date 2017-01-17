from ftw.upgrade import UpgradeStep


class IntroduceNewAPIUserRole(UpgradeStep):
    """Introduce new APIUser role.
    """

    def __call__(self):
        self.install_upgrade_profile()
