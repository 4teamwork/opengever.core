from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker


class ReindexSearchableTextToIncludeFilingNo(UpgradeStep):
    """Reindex searchable text to include filing no.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IFilingNumberMarker.__identifier__}
        for dossier in self.objects(query, 'Reindex searchable text to include filing no.'):
            if IFilingNumber(dossier).filing_no:
                # SearchableText is not in the catalog, so to avoid reindexing the
                # full object, we also reindex the UID.
                dossier.reindexObject(idxs=['UID', 'SearchableText'])
