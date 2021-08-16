from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
from ftw.upgrade.utils import SavepointIterator
from opengever.base.interfaces import IReferenceNumber
from plone.dexterity.interfaces import IDexterityContent


class UpdateReindexReferenceAndSortableReferenceIndex(UpgradeStep):
    """Update/reindex reference and sortable_reference index.
    """

    deferrable = True

    def __call__(self):
        self.index_sortable_reference_number()

    def index_sortable_reference_number(self):
        brains = self.catalog_unrestricted_search(
            {'object_provides': IDexterityContent.__identifier__})
        iterator = SavepointIterator.build(brains)
        message = 'Reindex reference'
        for brain in ProgressLogger(message, iterator):
            # update catalog but only if necessary
            obj = self.catalog_unrestricted_get_object(brain)
            if IReferenceNumber(obj).get_number() != brain.reference:
                obj.reindexObject(idxs=['reference', 'sortable_reference'])
