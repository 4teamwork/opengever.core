from BTrees.IIBTree import IITreeSet
from opengever.disposition import DISPOSITION_ACTIVE_STATES
from opengever.disposition.activities import DispositionAddedActivity
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IDisposition
from opengever.nightlyjobs.provider import NightlyJobProviderBase
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class NightlySIPDelivery(NightlyJobProviderBase):
    """Nightly job provider that delivers SIP packages scheduled for delivery.
    """

    def __init__(self, context, request, logger):
        super(NightlySIPDelivery, self).__init__(context, request, logger)

        self.catalog = api.portal.get_tool('portal_catalog')

    def _get_dispositions_for_delivery(self):
        """Get all dispositions that are in status 'disposed' and have a SIP.
        """
        query = dict(
            object_provides=IDisposition.__identifier__,
            review_state='disposition-state-disposed',
        )
        brains = self.catalog.unrestrictedSearchResults(query)
        for brain in brains:
            disposition = brain.getObject()
            if disposition.is_scheduled_for_delivery():
                yield disposition

    def __iter__(self):
        return iter(list(self._get_dispositions_for_delivery()))

    def __len__(self):
        return len(list(self._get_dispositions_for_delivery()))

    def run_job(self, job, interrupt_if_necessary):
        disposition = job
        self.logger.info("Delivering SIP for %r" % disposition)
        DeliveryScheduler(disposition, parent_logger=self.logger).deliver()


DOSSIER_JOURNAL_PDF_JOBS_KEY = 'opengever.disposition.nightly_jobs.dossier_journal_pdf'


class NightlyDossierJournalPDF(NightlyJobProviderBase):
    """Nightly job provider that creates journal PDFs for offered dossiers.
    """

    def __init__(self, context, request, logger):
        super(NightlyDossierJournalPDF, self).__init__(context, request, logger)
        self.intids = getUtility(IIntIds)

    def get_queue(self):
        """The queue is an IITreeSet in the site root's annotations.

        It contains the IntIds of dossiers that have been offered and still
        need their journal PDF to be created (or updated).
        """
        ann = IAnnotations(self.context)
        queue = ann.get(DOSSIER_JOURNAL_PDF_JOBS_KEY, [])
        return queue

    def __iter__(self):
        """Iterate over jobs, which as described above, are dossier IntIds.
        """
        queue = self.get_queue()

        # Avoid list size changing during iteration
        jobs = list(queue)

        for job in jobs:
            yield job

    def __len__(self):
        return len(self.get_queue())

    def queue_journal_pdf_job(self, dossier):
        """Queue a new journal PDF job for `dossier`.
        """
        dossier_intid = self.intids.getId(dossier)

        assert IPloneSiteRoot.providedBy(self.context)
        ann = IAnnotations(self.context)
        if DOSSIER_JOURNAL_PDF_JOBS_KEY not in ann:
            ann[DOSSIER_JOURNAL_PDF_JOBS_KEY] = IITreeSet()
        queue = ann[DOSSIER_JOURNAL_PDF_JOBS_KEY]

        queue.add(dossier_intid)

    def run_job(self, job, interrupt_if_necessary):
        """Run the job for the dossier identified by the IntId `job`.
        """
        dossier = self.intids.queryObject(job)
        if dossier is not None:
            self.logger.info("Creating journal PDF for %r" % dossier)
            dossier.create_or_update_journal_pdf()

        queue = self.get_queue()
        queue.remove(job)


class NightlyDossierPermissionSetter(NightlyJobProviderBase):
    """Nightly job provider that sets permissions for archivists on offered dossiers
    """

    def __init__(self, context, request, logger):
        super(NightlyDossierPermissionSetter, self).__init__(context, request, logger)
        self.catalog = api.portal.get_tool('portal_catalog')

    def maybe_commit(self, job):
        pass

    def _get_dispositions_with_pending_permissions_changes(self):
        """Get all dispositions that are in status 'disposed' and have a SIP.
        """
        query = dict(
            object_provides=IDisposition.__identifier__,
            review_state=DISPOSITION_ACTIVE_STATES,
        )
        brains = self.catalog.unrestrictedSearchResults(query)
        for brain in brains:
            disposition = brain.getObject()
            if not disposition.has_dossiers_with_pending_permissions_changes:
                continue
            yield disposition

    def __iter__(self):
        return iter(list(self._get_dispositions_with_pending_permissions_changes()))

    def __len__(self):
        return len(list(self._get_dispositions_with_pending_permissions_changes()))

    def run_job(self, job, interrupt_if_necessary):
        disposition = job
        self.logger.info("Setting permissions on dossiers for %r" % disposition)
        while disposition.dossiers_with_missing_permissions:
            uid = disposition.dossiers_with_missing_permissions.pop()
            dossier = uuidToObject(uid)
            if dossier is not None:
                disposition.give_view_permissions_to_archivists_on_dossier(dossier)
            transaction.commit()
            self.logger.info("Added permissions on %r" % dossier)

        while disposition.dossiers_with_extra_permissions:
            uid = disposition.dossiers_with_extra_permissions.pop()
            dossier = uuidToObject(uid)
            if dossier is not None:
                disposition.revoke_view_permissions_from_archivists_on_dossier(dossier)
            transaction.commit()
            self.logger.info("Added permissions on %r" % dossier)

        if not disposition.creation_activity_recorded:
            DispositionAddedActivity(disposition, self.request).record()
            disposition.creation_activity_recorded = True
            transaction.commit()
        self.logger.info("Finished setting permissions for %r" % disposition)
