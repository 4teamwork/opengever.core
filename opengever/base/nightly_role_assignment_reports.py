from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import ASSIGNMENT_VIA_PROTECT_DOSSIER
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.storage import STATE_IN_PROGRESS
from opengever.base.storage import STATE_READY
from opengever.nightlyjobs.provider import NightlyJobProviderBase
from plone import api
from zope.component.hooks import getSite
from zope.component.hooks import setSite
import gc


class NightlyRoleAssignmentReports(NightlyJobProviderBase):

    def __init__(self, context, request, logger):
        super(NightlyRoleAssignmentReports, self).__init__(context, request, logger)

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
        principalid = job['principal_id']
        reportid = job['report_id']
        items = []

        # if Anonymous or Authenticated have View permission,
        # no other users are set in allowedRolesAndUsers
        brains = self.catalog.unrestrictedSearchResults(
            sort_on='path',
            portal_type=['opengever.dossier.businesscasedossier',
                         'opengever.repository.repositoryfolder',
                         'opengever.repository.repositoryroot',
                         'opengever.workspace.folder',
                         'opengever.workspace.workspace',
                         ],
            allowedRolesAndUsers=[u'user:{}'.format(principalid), 'Authenticated', 'Anonymous'])

        self.logger.info("Complete report %r" % reportid)

        for i, brain in enumerate(brains):
            if i % 5000 == 0:
                self.collect_garbage(self.context)
            obj = brain.getObject()
            assignments = RoleAssignmentManager(obj).get_assignments_by_principal_id(principalid)
            manual_assignments = [
                assignment for assignment in assignments
                if assignment.cause in [ASSIGNMENT_VIA_SHARING,
                                        ASSIGNMENT_VIA_PROTECT_DOSSIER,
                                        ASSIGNMENT_VIA_INVITATION]]
            if manual_assignments:
                roles = filter(lambda r: r != 'Owner', manual_assignments[0].roles)
                if roles:
                    items.append({'UID': obj.UID(), 'roles': roles})

        report_data = {'state': STATE_READY, 'items': items}
        self.storage.update(reportid, report_data)
