from ftw.upgrade import UpgradeStep


class OptimizeSimpleSearchTermPattern(UpgradeStep):
    """Optimize simple_search_term_pattern.
    """

    def __call__(self):
        self.install_upgrade_profile()
