from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import IReferenceNumberPrefix


def regenerate_and_reindex_reference_number(obj):
    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)

    prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference'])

    for child in obj.objectValues():
        regenerate_and_reindex_reference_number(child)


class RegenerateAndReindexReferenceNumbersOnPrivateRootsAndTheirContents(UpgradeStep):
    """Regenerate and reindex reference numbers on private roots and their contents."""

    def __call__(self):
        query = {'portal_type': 'opengever.private.root'}

        for obj in self.objects(query, 'Regenerate and reindex reference numbers on private roots and their contents.'):
            regenerate_and_reindex_reference_number(obj)
