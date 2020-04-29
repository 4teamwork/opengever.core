from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker


class AddIsSubdossierToCatalogMetadata(UpgradeStep):
    """Add is_subdossier to catalog metadata.

    We purposefully only reindex dossiers to make sure metadata is updated
    since those are the only types where it should be truly relevant.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        query = {
            'object_provides': [IDossierMarker.__identifier__,
                                IDossierTemplateMarker.__identifier__]
            }
        # To avoid reindexing the whole objects, we pick any index that exists
        # for all objects and is fast to compute.
        # is_subdossier is already a solr field, so we don't need to pass it
        # as an index here.
        self.catalog_reindex_objects(query, idxs=['UID'])
