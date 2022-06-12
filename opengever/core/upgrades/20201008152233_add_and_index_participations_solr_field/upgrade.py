from ftw.upgrade import UpgradeStep


class AddAndIndexParticipationsSolrField(UpgradeStep):
    """Add and index participations solr field.
    """
    deferrable = True

    def __call__(self):
        # Disable this upgradestep because the reindexObject for all
        # Participatationobjects (dossiers) have been moved to a later upgradestep
        # 20210128083955_index_blocked_local_roles_in_solr_for_repository_folders_and_dossiers

        return
        # query = {'object_provides': IParticipationAwareMarker.__identifier__}
        # for dossier in self.objects(query, 'Index participations field in solr.'):
        #     # participations is only in solr, prevent reindexing all catalog
        #     # indexes by picking a cheap catalog index `UID`.
        #     dossier.reindexObject(idxs=['UID', 'participations'])
