from ftw.upgrade import UpgradeStep


class AddSequenceNumberToSolrPattern(UpgradeStep):
    """Add sequence number to solr pattern.
    """

    def __call__(self):
        self.install_upgrade_profile()
