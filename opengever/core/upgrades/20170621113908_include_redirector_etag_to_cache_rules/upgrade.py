from ftw.upgrade import UpgradeStep


class IncludeRedirectorEtagToCacheRules(UpgradeStep):
    """Include redirector etag to cache rules.
    """

    def __call__(self):
        self.install_upgrade_profile()
