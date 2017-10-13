from ftw.upgrade import UpgradeStep


class RegisterTableRadioWidgetJs(UpgradeStep):
    """Register TableRadioWidget.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
