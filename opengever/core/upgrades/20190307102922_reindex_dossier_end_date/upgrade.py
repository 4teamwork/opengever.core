from ftw.upgrade import UpgradeStep


class ReindexDossierEndDate(UpgradeStep):
    """Reindex dossier end date when there is a mismatch between index and metadata
    """

    def __call__(self):
        query = {'object_provides': 'opengever.dossier.behaviors.dossier.IDossierMarker'}
        catalog = self.portal.portal_catalog
        end = catalog._catalog.getIndex("end")
        for brain in self.catalog_unrestricted_search(query):
            end_metadata = brain.end
            end_index = end.getEntryForObject(brain.getRID(), "")
            if (end_metadata or end_index) and not (end_metadata and end_index):
                brain.getObject().reindexObject(idxs=['end'])
