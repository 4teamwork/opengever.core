from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.participation import IParticipationAwareMarker


class AddAndIndexParticipationsSolrField(UpgradeStep):
    """Add and index participations solr field.
    """
    deferrable = True

    def __call__(self):
        query = {'object_provides': IParticipationAwareMarker.__identifier__}
        for dossier in self.objects(query, 'Index participations field in solr.'):
            # participations is only in solr, prevent reindexing all catalog
            # indexes by picking a cheap catalog index `UID`.
            dossier.reindexObject(idxs=['UID', 'participations'])
