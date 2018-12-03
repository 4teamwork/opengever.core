from ftw.upgrade import UpgradeStep
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.task.localroles import LocalRolesSetter
from opengever.task.task import ITask
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class AddProposalRoleAssignments(UpgradeStep):
    """Add proposal role assignments.

    Instead of iterating over all tasks or documents we start at the
    proposal side assuming that there are fewer proposals than tasks or
    documents.
    Also that way the migration will only run for deployments that have meeting
    content, so there is no need to check against the feature flag.
    """

    deferrable = True

    def __call__(self):
        msg = 'Add role assignments to proposals referenced by tasks'
        query = {'portal_type': 'opengever.meeting.proposal'}

        for proposal in self.objects(query, msg):
            self.add_role_assignments(proposal)

    def add_role_assignments(self, proposal):
        document = proposal.get_proposal_document()

        # should not be possible to happen, but proposals without document
        # cannot be referenced by tasks thus no need to worry about that in
        # this upgrade.
        if not document:
            return

        relation_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)

        query = {'to_id': intids.getId(document)}
        relations = relation_catalog.findRelations(query)
        for relation in relations:
            if ITask.providedBy(relation.from_object):
                task = relation.from_object
                self.add_role_assignment_to_proposal(document, task)

    def add_role_assignment_to_proposal(self, document, task):
        document_manager = RoleAssignmentManager(document)
        # abort if we do not have an assignment for local roles in the
        # document. it might be this is one of the migrated tasks where the
        # assignment has only been set for sharing but not based on the local
        # roles for the tasks.
        if not document_manager.get_assignments_by_cause(ASSIGNMENT_VIA_TASK):
            return

        # if we have an assignment it should be safe to set the assignment
        # again as would happen when the task has been modified.
        LocalRolesSetter(task).set_roles(event=None)
