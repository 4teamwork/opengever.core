from ftw.upgrade import UpgradeStep


class IncludeOrgunitSelectorETagToCacheRules(UpgradeStep):
    """Include orgunit selector eTag to cache rules.
    """

    def __call__(self):
        self.install_upgrade_profile()
