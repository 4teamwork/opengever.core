from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.resolve import AfterResolveJobs
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


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
        return iter([{'path': brain.getPath()} for brain in pending])

    def __len__(self):
        resultset = self.catalog.unrestrictedSearchResults(self.query)
        return resultset.actual_result_count

    def run_job(self, job, interrupt_if_necessary):
        path = job['path']
        dossier = self.context.unrestrictedTraverse(path)
        self.logger.info("Running AfterResolve jobs for %r" % dossier)
        AfterResolveJobs(dossier).execute(nightly_run=True)
