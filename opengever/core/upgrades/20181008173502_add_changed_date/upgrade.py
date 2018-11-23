from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.changed import METADATA_CHANGED_FILLED_KEY
from zope.annotation import IAnnotations
from zope.component.hooks import getSite
import copy


class AddChangedDate(UpgradeStep):
    """Add changed date field, metadata and index.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.add_changed_index()
        self.set_changed_flag()

    def add_changed_index(self):
        """ We fill the index by copying the data from the 'modified' index,
        as this is much faster than indexing every object. The 'DateIndex'
        object has a forward ('_index') and backward ('_unindex') index inherited
        from UnIndex containing data of the form:
            _index = {datum:[record_id, documentId2]}
            _unindex = {record_id:datum}

        as 'record_id' are the same for all indexes and come from the catalog ('getRID'),
        it should be safe to simply copy the data contained in '_index' and '_unindex'.

        the _length attribute stores the number of entries in the index and
        also needs to be updated.
        These three attributes contain all the data of the index. The 'clear'
        method of the index simply resets these three attributes.
        """
        self.catalog_add_index('changed', 'DateIndex')

        catalog = self.getToolByName('portal_catalog')
        modified = catalog._catalog.indexes["modified"]
        changed = catalog._catalog.indexes["changed"]

        changed._index.update(copy.deepcopy(modified._index))
        changed._unindex.update(copy.deepcopy(modified._unindex))
        changed._length.set(modified._length.value)

    def set_changed_flag(self):
        site = getSite()
        annotations = IAnnotations(site)
        annotations[METADATA_CHANGED_FILLED_KEY] = False
