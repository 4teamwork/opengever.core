from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer


class ReindexMailReferenceNumbers(UpgradeStep):
    """Reindex mail reference numbers.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}

        with NightlyIndexer(idxs=["reference", "sortable_reference", "metadata"]) as indexer:
            for brain in self.brains(query, 'Queueing mail reference number reindexing job'):
                indexer.add_by_brain(brain)
