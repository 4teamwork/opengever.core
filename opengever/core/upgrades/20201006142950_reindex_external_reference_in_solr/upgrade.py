from ftw.upgrade import UpgradeStep


class ReindexExternalReferenceInSolr(UpgradeStep):
    """Reindex external_reference for objects in solr.

    The field IDocumentMetadata.foreign_reference is also indexed into the
    index external_reference. We include it here to reindex consistently.

    Only objects with an actual value are reindexed, only a mininal amount of
    objects in production seem to have a value.

    """
    deferrable = True

    def __call__(self):
        query = {'external_reference': {'not': [None, '']}}

        for obj in self.objects(
                query, 'Reindex external_reference in solr'):
            obj.reindexObject(idxs=['external_reference'])
