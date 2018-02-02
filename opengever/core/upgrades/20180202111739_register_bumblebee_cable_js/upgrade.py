from ftw.upgrade import UpgradeStep


class RegisterBumblebeeCableJs(UpgradeStep):
    """Register bumblebee cable js.
    """

    def __call__(self):
        self.install_upgrade_profile()
