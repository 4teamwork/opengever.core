from opengever.base.role_assignments import RoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from Products.Five.browser import BrowserView
import json


class ManageRoleAssignmentsView(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')

        manager = RoleAssignmentManager(self.context)
        assignments = [RoleAssignment.get(**data)
                       for data in manager.storage._storage()]

        return json.dumps(
            [assignment.serialize() for assignment in assignments])
