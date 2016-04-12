from ftw.upgrade import UpgradeStep


class EnableRequestContentNegotiation(UpgradeStep):
    """Language Tool: Enable request content negotiation.
    """

    def __call__(self):
        self.install_upgrade_profile()
