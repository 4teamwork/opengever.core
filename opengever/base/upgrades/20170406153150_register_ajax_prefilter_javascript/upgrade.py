from ftw.upgrade import UpgradeStep


class RegisterAjaxPrefilterJavascript(UpgradeStep):
    """Register ajax prefilter javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
