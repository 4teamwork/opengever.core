from ftw.upgrade import UpgradeStep
from opengever.base.behaviors.classification import IClassification
from opengever.core.upgrade import DefaultValuePersister
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.nightlyjobs.maintenance_jobs import QueueIsMissing
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import logging


log = logging.getLogger('ftw.upgrade')

classification = IClassification.get("classification")
privacy_layer = IClassification.get("privacy_layer")
public_trial = IClassification.get("public_trial")

preserved_as_paper = IDocumentMetadata.get("preserved_as_paper")


class MigrateDefaultValuePersisterMaintenanceJobs(UpgradeStep):
    """Migrate default value persister maintenance jobs.
    """

    def __call__(self):
        # migrate jobs for 20211026132727_persist_missing_classification_fields
        fields = (classification, privacy_layer, public_trial)
        persister = DefaultValuePersister(fields=fields)
        self.migrate_queue(persister)

        # migrate jobs for 20211026132728_persist_missing_preserved_as_paper
        fields = (preserved_as_paper, )
        persister = DefaultValuePersister(fields=fields)
        self.migrate_queue(persister)

    def migrate_queue(self, persister):
        try:
            queue = persister.queue_manager.get_queue(persister.job_type)
        except QueueIsMissing:
            return
        if isinstance(queue['queue'], persister.queue_type):
            return

        intids = getUtility(IIntIds)
        old_queue = persister.queue_manager.remove_queue(persister.job_type)['queue']
        njobs = len(old_queue)
        log.info("Migrating {} jobs for {}".format(njobs, persister.job_type))
        with persister:
            for i, intid in enumerate(old_queue, 1):
                if i % 1000 == 0:
                    log.info("Done migrating {} / {} jobs".format(i, njobs))
                obj = intids.queryObject(intid)
                if not obj:
                    continue
                persister.add_by_obj(obj)
