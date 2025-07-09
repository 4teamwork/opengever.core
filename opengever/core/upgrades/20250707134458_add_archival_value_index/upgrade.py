from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.lifecycle import ILifeCycleMarker
from opengever.core.upgrade import NightlyIndexer


class AddArchivalValueIndex(UpgradeStep):
    """Add archival value index.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': [
            ILifeCycleMarker.__identifier__,
        ]}

        with NightlyIndexer(idxs=["archival_value"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index archival_value in Solr'):
                indexer.add_by_brain(brain)
