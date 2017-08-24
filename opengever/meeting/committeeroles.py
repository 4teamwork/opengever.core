class CommitteeRoles(object):
    """Sets local roles committees for a principal.

    Preserves other roles that are set for the principal.

    There is currently one special role CommitteeResponsible. This role will
    be added as local role on a committee for the group that can be selected
    in the add/edit forms.

    """
    managed_roles = ('CommitteeResponsible', 'Editor', 'Reader')

    def __init__(self, committee):
        self.context = committee

    def _add_managed_local_roles(self, principal):
        """Add managed roles to context for principal."""
        if isinstance(principal, unicode):
            principal = principal.encode('utf8')

        self.context.manage_addLocalRoles(principal, self.managed_roles)

    def _drop_managed_local_roles(self, principal):
        """Removes managed roles from context but preserves other, manually
        added roles for principal.

        """
        current_roles = dict(self.context.get_local_roles()).get(principal, ())
        new_roles = list(set([role for role in current_roles
                              if role not in self.managed_roles]))
        if new_roles:
            self.context.manage_setLocalRoles(principal, new_roles)
        else:
            self.context.manage_delLocalRoles([principal])

    def initialize(self, principal):
        """Initialize local roles by adding managed roles for principal."""

        if not principal:
            return

        self._add_managed_local_roles(principal)
        self.context.reindexObjectSecurity()

    def update(self, principal, previous_principal):
        """Update local roles by adding managed roles for principal and dropping
        managed roles for previous_principal.

        """
        if principal == previous_principal:
            return

        if previous_principal:
            self._drop_managed_local_roles(previous_principal)
        self._add_managed_local_roles(principal)
        self.context.reindexObjectSecurity()
