from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.nightlyjobs.maintenance_jobs import QueueIsMissing
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import logging


log = logging.getLogger('ftw.upgrade')


class MigrateNightlyIndexerMaintenanceJobs(UpgradeStep):
    """Migrate nightly indexer maintenance jobs.
    """

    def __call__(self):
        # migrate jobs for 20210205084521_add_sortable_reference_number_index
        indexer = NightlyIndexer(idxs=["sortable_reference"],
                                 index_in_solr_only=True)
        self.migrate_queue(indexer)

        # migrate jobs for 20211102201059_reindex_is_completed_for_tasks_and_todos
        indexer = NightlyIndexer(idxs=["is_completed"],
                                 index_in_solr_only=True)
        self.migrate_queue(indexer)

        # migrate jobs for 20211221135724_add_dossier_type_index
        indexer = NightlyIndexer(idxs=["dossier_type"],
                                 index_in_solr_only=True)
        self.migrate_queue(indexer)

    def migrate_queue(self, indexer):
        try:
            queue = indexer.queue_manager.get_queue(indexer.job_type)
        except QueueIsMissing:
            return
        if isinstance(queue['queue'], indexer.queue_type):
            return

        intids = getUtility(IIntIds)
        old_queue = indexer.queue_manager.remove_queue(indexer.job_type)['queue']
        njobs = len(old_queue)
        log.info("Migrating {} jobs for {}".format(njobs, indexer.job_type))
        with indexer:
            for i, intid in enumerate(old_queue, 1):
                if i % 1000 == 0:
                    log.info("Done migrating {} / {} jobs".format(i, njobs))
                obj = intids.queryObject(intid)
                if not obj:
                    continue
                indexer.add_by_obj(obj)
