from ftw.upgrade import UpgradeStep


class AddNewIndexRetentionExpiration(UpgradeStep):
    """Add new index retention_expiration.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_add_index('retention_expiration', 'DateIndex')

    # The calculation of the retention period has been changed, because of
    # that there is another upgrade step `UpdateRetentionPeriodCalculation`
    # which recalculate the retention expiration for every resolved dossier.
    # Therefore the reindex for those dossiers is not necessary ann will be
    # done by the newer upgradestep `UpdateRetentionPeriodCalculation`

    # def reindex_resolved_dossiers(self):
    #     for obj in self.objects(
    #             {'object_provides': IDossierMarker.__identifier__,
    #              'review_state': 'dossier-state-resolved'},
    #             'Enable exclude from navigation for files'):

    #         obj.reindexObject(idxs=['retention_expiration'])
