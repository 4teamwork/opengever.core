from BTrees.IIBTree import IITreeSet
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IDisposition
from opengever.nightlyjobs.provider import NightlyJobProviderBase
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


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
        dossier = self.intids.getObject(job)

        self.logger.info("Creating journal PDF for %r" % dossier)
        dossier.create_or_update_journal_pdf()

        queue = self.get_queue()
        queue.remove(job)
