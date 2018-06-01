from ftw.upgrade import UpgradeStep


class RemoveTrixAndProtocolJavascripts(UpgradeStep):
    """Remove trix and protocol javascripts.
    """

    def __call__(self):
        self.install_upgrade_profile()
