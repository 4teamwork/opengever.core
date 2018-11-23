from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.changed import METADATA_CHANGED_FILLED_KEY
from zope.annotation import IAnnotations
from zope.component.hooks import getSite


class AddChangedDateV2(UpgradeStep):
    """Add changed date field, metadata and index (V2).

    This upgrade step was updated and touched.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.add_changed_index()
        self.set_changed_flag()

    def add_changed_index(self):
        """The idea is to fill the new "changed" index with the value of the "modified"
        index as this is the best value we now from older objects which do not have
        a separate changed date.

        The "changed" index is populated by iterating over the data of the "modified" index
        and inserting them in the "changed" index.
        Since we are just inserting already converted values in the form they are stored
        in the index and are not using a full object for inexing, we need to directly
        put the values into the DateIndexes "index" and "unindex" BTree.
        We do that the same way as DateIndex.index_object inserts data.

        Warning: This upgrade step has an earlier incarnation which was installed on
        some installation (dev, test). We want this upgrade to be reran.
        """
        if not self.catalog_has_index('changed'):
            self.catalog_add_index('changed', 'DateIndex')

        catalog = self.getToolByName('portal_catalog')
        modified = catalog._catalog.indexes["modified"]
        changed = catalog._catalog.indexes["changed"]

        for documentId, value in modified.documentToKeyMap().items():
            changed.insertForwardIndexEntry(value, documentId)
            changed._unindex[documentId] = value

    def set_changed_flag(self):
        site = getSite()
        annotations = IAnnotations(site)
        annotations[METADATA_CHANGED_FILLED_KEY] = False
