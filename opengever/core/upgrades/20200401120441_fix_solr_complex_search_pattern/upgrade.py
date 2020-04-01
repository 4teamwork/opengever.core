from ftw.upgrade import UpgradeStep


class FixSolrComplexSearchPattern(UpgradeStep):
    """Fix solr complex search pattern.
    """

    def __call__(self):
        self.install_upgrade_profile()
