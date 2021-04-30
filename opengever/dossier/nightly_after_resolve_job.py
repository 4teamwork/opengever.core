from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.resolve import AfterResolveJobs
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


MAX_CONVERSION_REQUESTS_PER_NIGHT = 10000

# Track total number of conversion requests sent per nightly run
sent_conversion_requests = 0


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class ExecuteNightlyAfterResolveJobs(object):

    def __init__(self, context, request, logger):
        self.context = context
        self.request = request
        self.logger = logger

        self.catalog = api.portal.get_tool('portal_catalog')

        # Get all dossiers that are resolved, but still have
        # AfterResolveJobs pending
        self.query = dict(
            object_provides=IDossierMarker.__identifier__,
            review_state='dossier-state-resolved',
            after_resolve_jobs_pending=True,
        )

    def __iter__(self):
        pending = self.catalog.unrestrictedSearchResults(self.query)
        for brain in pending:
            self.logger.info('sent_conversion_requests: {}'.format(
                sent_conversion_requests))
            if sent_conversion_requests >= MAX_CONVERSION_REQUESTS_PER_NIGHT:
                self.logger.warn(
                    "Reached MAX_CONVERSION_REQUESTS_PER_NIGHT "
                    "(%r) limit, stopping after resolve jobs for tonight." %
                    MAX_CONVERSION_REQUESTS_PER_NIGHT)
                raise StopIteration
            yield {'path': brain.getPath()}

    def __len__(self):
        resultset = self.catalog.unrestrictedSearchResults(self.query)
        return resultset.actual_result_count

    def run_job(self, job, interrupt_if_necessary):
        global sent_conversion_requests
        path = job['path']
        dossier = self.context.unrestrictedTraverse(path)
        self.logger.info("Running AfterResolve jobs for %r" % dossier)
        after_resolve_jobs = AfterResolveJobs(dossier)
        after_resolve_jobs.execute(nightly_run=True)
        sent_conversion_requests += after_resolve_jobs.num_pdf_conversions
