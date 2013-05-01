from ftw.upgrade import UpgradeStep


class RegisterJavascript(UpgradeStep):
    """Register the download confirmation javascript."""

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.document.upgrades:2301')
