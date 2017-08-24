from ftw.upgrade import UpgradeStep


class ReplaceCommitteeGroupMemberRole(UpgradeStep):
    """Replace CommitteeGroupMember role.

    The role is replaced with CommitteeResponsible which has approximately
    the same permissions as CommitteeGroupMember used to have and
    CommitteeMember which can only view (at the moment).

    The Editor role is necessary at the moment due to document workflow
    permission assignment. Without Editor the responsible does not have the
    necessary CMFEditions* permissions.
    The Reader role is necessary at the moment due to mail workflow
    permission assignment.

    CommitteeMember is not assigned automatically for now, so no migration is
    necessary.
    """

    role_to_remove = 'CommitteeGroupMember'
    roles_to_add = ('CommitteeResponsible', 'Editor', 'Reader')

    def __call__(self):
        self.remove_role()
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_submitted_proposal_workflow'], reindex_security=False)
        self.reapply_committee_local_role()

    def remove_role(self):
        """Remove a role from the plone site.

        Removes a role from the role list kept in the plone site and also
        from the (somehow separate) list of roles that are managed by
        portal_role_manager.

        Also see ZODBRoleManager.removeRole for more information.
        """
        self.portal._delRoles([self.role_to_remove])

        role_manager = self.portal.acl_users.portal_role_manager
        if self.role_to_remove in list(role_manager.listRoleIds()):
            role_manager.removeRole(self.role_to_remove)

    def reapply_committee_local_role(self):
        query = {'portal_type': 'opengever.meeting.committee'}
        for committee in self.objects(query, 'update committee local roles'):
            group_id = committee.load_model().group_id

            current_roles = dict(committee.get_local_roles()).get(group_id, ())
            roles_to_keep = set(role for role in current_roles
                                if role != self.role_to_remove)
            new_roles = roles_to_keep.union(set(self.roles_to_add))
            committee.manage_setLocalRoles(group_id, list(new_roles))
            committee.reindexObjectSecurity()
