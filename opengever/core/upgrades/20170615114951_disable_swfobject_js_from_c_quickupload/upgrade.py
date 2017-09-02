from ftw.upgrade import UpgradeStep


class DisableSwfobjectJsFromCQuickupload(UpgradeStep):
    """Disable swfobject.js from c.quickupload.
    """

    def __call__(self):
        self.install_upgrade_profile()
