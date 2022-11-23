from ftw.upgrade import UpgradeStep
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentStorage


class UpdateTaskAssignmentRole(UpgradeStep):
    """Update task assignment role.
    There is no need to reindex the security indexes as view permissions
    were not changed. We therefore do the update directly using the
    RoleAssignmentManager.
    """

    deferrable = True

    def __call__(self):
        query = {
            'object_provides': [
                'opengever.dossier.behaviors.dossier.IDossierMarker',
                'opengever.inbox.inbox.IInbox'
            ]
        }
        for obj in self.objects(query, "Update task assignments."):
            storage = RoleAssignmentStorage(obj)
            for assignment in storage.get_by_cause(ASSIGNMENT_VIA_TASK):
                self.update_assignment(assignment)
            for assignment in storage.get_by_cause(ASSIGNMENT_VIA_TASK_AGENCY):
                self.update_assignment(assignment)

    @staticmethod
    def update_assignment(assignment):
        if 'Contributor' in assignment['roles']:
            assignment['roles'].remove('Contributor')
            assignment['roles'].append('TaskResponsible')
