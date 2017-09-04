from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker


INDEX_NAME = 'is_subdossier'


class ReplaceIsSubdossierFieldIndexWithABooleanIndex(UpgradeStep):
    """Replace is_subdossier field index with a boolean index.
    """

    def __call__(self):
        self.catalog_remove_index(INDEX_NAME)
        self.catalog_add_index(INDEX_NAME, 'BooleanIndex')
        catalog = self.getToolByName('portal_catalog')

        for obj in self.objects({'object_provides': IDossierMarker.__identifier__},
                                'Reindex is_subdossier index'):

            catalog.reindexObject(
                obj, idxs=[INDEX_NAME], update_metadata=False)
