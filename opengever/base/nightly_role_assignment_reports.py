from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.storage import STATE_IN_PROGRESS
from opengever.base.storage import STATE_READY
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import gc
import logging


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class NightlyRoleAssignmentReports(object):

    def __init__(self, context, request, logger):
        self.context = context
        self.request = request
        self.logger = logger

        self.storage = IRoleAssignmentReportsStorage(self.context)
        self.catalog = api.portal.get_tool('portal_catalog')

    def __iter__(self):
        return iter([el for el in self.storage.list() if el['state'] == STATE_IN_PROGRESS])

    def __len__(self):
        return len([el for el in self.storage.list() if el['state'] == STATE_IN_PROGRESS])

    def collect_garbage(self, site):
        # In order to get rid of leaking references, the Plone site needs to be
        # re-set in regular intervals using the setSite() hook. This reassigns
        # it to the SiteInfo() module global in zope.component.hooks, and
        # therefore allows the Python garbage collector to cut loose references
        # it was previously holding on to.
        setSite(getSite())

        # Trigger garbage collection for the cPickleCache
        site._p_jar.cacheGC()

        # Also trigger Python garbage collection.
        gc.collect()

        # (These two don't seem to affect the memory high-water-mark a lot,
        # but result in a more stable / predictable growth over time.
        #
        # But should this cause problems at some point, it's safe
        # to remove these without affecting the max memory consumed too much.)

    def run_job(self, job, interrupt_if_necessary):
        principalid = job['principalid']
        reportid = job['reportid']
        items = []

        # if Anonymous or Authenticated have View permission,
        # no other users are set in allowedRolesAndUsers
        brains = self.catalog.unrestrictedSearchResults(
            portal_type=['opengever.dossier.businesscasedossier',
                         'opengever.repository.repositoryfolder',
                         'opengever.repository.repositoryroot'],
            allowedRolesAndUsers=[u'user:{}'.format(principalid), 'Authenticated', 'Anonymous'])

        self.logger.info("Complete report %r" % reportid)

        for i, brain in enumerate(brains):
            if i % 5000 == 0:
                self.collect_garbage(self.context)
            obj = brain.getObject()
            assignments = RoleAssignmentManager(obj).get_assignments_by_principal_id(principalid)
            sharing_assignments = [assignment for assignment in assignments
                                   if assignment.cause == ASSIGNMENT_VIA_SHARING]
            if sharing_assignments:
                items.append({'UID': obj.UID(), 'roles': sharing_assignments[0].roles})

        report_data = {'state': STATE_READY, 'items': items}
        self.storage.update(reportid, report_data)
