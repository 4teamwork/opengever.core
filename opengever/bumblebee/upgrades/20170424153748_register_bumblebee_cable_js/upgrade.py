from ftw.upgrade import UpgradeStep


class RegisterBumblebeeCableJs(UpgradeStep):
    """Register BumblebeeCable js.
    """

    def __call__(self):
        self.install_upgrade_profile()
