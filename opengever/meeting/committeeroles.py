from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import CommitteeGroupAssignment


class CommitteeRoles(object):
    """Sets local roles committees for a principal.

    Preserves other roles that are set for the principal.

    There is currently one special role CommitteeResponsible. This role will
    be added as local role on a committee for the group that can be selected
    in the add/edit forms.

    """
    managed_roles = ('CommitteeResponsible',)

    def __init__(self, committee):
        self.context = committee

    def _add_managed_local_roles(self, principal):
        """Add managed roles to context for principal."""
        if isinstance(principal, unicode):
            principal = principal.encode('utf8')

        assignment = CommitteeGroupAssignment(
            principal, self.managed_roles, self.context)
        RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

    def initialize(self, principal):
        """Initialize local roles by adding managed roles for principal."""

        if not principal:
            return

        self._add_managed_local_roles(principal)

    def update(self, principal, previous_principal):
        """Update local roles by adding managed roles for principal and dropping
        managed roles for previous_principal.

        """
        if principal == previous_principal:
            return

        assignments = [CommitteeGroupAssignment(
            principal, self.managed_roles, self.context)
        ]
        RoleAssignmentManager(self.context).set(assignments)
