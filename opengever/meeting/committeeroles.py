class CommitteeRoles(object):
    """Sets roles for committees based on an ogds group.

    The roles that are managed currently are 'Reader', 'Contributor' and
    'Editor'. These roles will be added for the group that can be selected in
    the add/edit forms.

    Caution: this may conflict with roles that are set manually.
    """

    # XXX: Replace with proper CommitteeMember role
    roles = ('Reader', 'Contributor', 'Editor')

    def __init__(self, group_id, previous_group_id=None):
        self.group_id = group_id
        self.previous_group_id = previous_group_id

    def _add_local_roles(self, context, principal, roles):
        """Adds managed roles to context."""

        current_roles = dict(context.get_local_roles()).get(principal, ())
        new_roles = list(set(list(current_roles) + list(roles)))
        context.manage_setLocalRoles(principal, new_roles)

    def _drop_local_roles(self, context, principal, roles):
        """Removes managed roles from context."""

        current_roles = dict(context.get_local_roles()).get(principal, ())
        new_roles = list(set([role for role in current_roles
                              if role not in self.roles]))
        if new_roles:
            context.manage_setLocalRoles(principal, new_roles)
        else:
            context.manage_delLocalRoles([principal])

    def initialize(self, committee):
        """Initialize local roles for a committee."""

        committee.__ac_local_roles_block__ = True
        self.update(committee)

    def update(self, committee):
        """Update local roles for a committee."""

        if self.previous_group_id:
            self._drop_local_roles(committee, self.previous_group_id,
                                   self.roles)
        self._add_local_roles(committee, self.group_id, self.roles)

        committee.reindexObjectSecurity()
