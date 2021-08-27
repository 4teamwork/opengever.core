from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContent
from opengever.core.upgrade import NightlyIndexer


class AddSortableReferenceNumberIndex(UpgradeStep):
    """Add sortable reference number index.
    """

    deferrable = True

    def __call__(self):
        self.index_sortable_reference_number()

    def index_sortable_reference_number(self):
        query = {'object_provides': IDexterityContent.__identifier__}
        with NightlyIndexer(idxs=["sortable_reference"],
                            index_in_solr_only=True) as indexer:
            for obj in self.objects(query, 'Index sortable_reference in Solr'):
                indexer.add_by_obj(obj)
