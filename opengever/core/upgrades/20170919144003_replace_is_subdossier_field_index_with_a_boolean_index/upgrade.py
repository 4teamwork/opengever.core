from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker


INDEX_NAME = 'is_subdossier'


class ReplaceIsSubdossierFieldIndexWithABooleanIndex(UpgradeStep):
    """Replace is_subdossier field index with a boolean index.
    """

    def __call__(self):
        self.catalog_remove_index(INDEX_NAME)
        self.catalog_add_index(INDEX_NAME, 'BooleanIndex')
        self.catalog_rebuild_index(INDEX_NAME)
