from zope.component import getMultiAdapter


class RepositoryMixin(object):

    def get_groupnames_with_local_role(self, rolename):
        return ','.join(set([
            group
            for group, roles in self.get_local_roles()
            for role in roles
            if role == rolename
        ]))

    def get_groupnames_with_local_or_inherited_role(self, rolename):
        groups = []
        sharing_view = getMultiAdapter((self, self.REQUEST), name="sharing")
        local_roles = sharing_view.role_settings()
        for role in local_roles:
            if role['computed_roles'].get(rolename):
                groups.append(role.get('id'))
        return groups

    def get_groupnames_with_local_reader_role(self):
        return self.get_groupnames_with_local_role('Reader')

    def get_groupnames_with_local_contributor_role(self):
        return self.get_groupnames_with_local_role('Contributor')

    def get_groupnames_with_local_editor_role(self):
        return self.get_groupnames_with_local_role('Editor')

    def get_groupnames_with_local_reviewer_role(self):
        return self.get_groupnames_with_local_role('Reviewer')

    def get_groupnames_with_local_publisher_role(self):
        return self.get_groupnames_with_local_role('Publisher')

    def get_groupnames_with_local_manager_role(self):
        return self.get_groupnames_with_local_role('Manager')

    def get_groupnames_with_local_taskresponsible_role(self):
        return self.get_groupnames_with_local_role('TaskResponsible')

    def get_groupnames_with_local_or_inherited_reader_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Reader')

    def get_groupnames_with_local_or_inherited_contributor_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Contributor')

    def get_groupnames_with_local_or_inherited_editor_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Editor')

    def get_groupnames_with_local_or_inherited_reviewer_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Reviewer')

    def get_groupnames_with_local_or_inherited_publisher_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Publisher')

    def get_groupnames_with_local_or_inherited_manager_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Manager')

    def get_groupnames_with_local_or_inherited_taskresponsible_role(self):
        return self.get_groupnames_with_local_or_inherited_role('TaskResponsible')
