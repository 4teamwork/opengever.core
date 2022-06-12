class RepositoryMixin(object):
    def get_groupnames_with_role(self, rolename):
        return ','.join(set([
            group
            for group, roles in self.get_local_roles()
            for role in roles
            if role == rolename
        ]))

    def get_groupnames_with_reader_role(self):
        return self.get_groupnames_with_role('Reader')

    def get_groupnames_with_contributor_role(self):
        return self.get_groupnames_with_role('Contributor')

    def get_groupnames_with_editor_role(self):
        return self.get_groupnames_with_role('Editor')

    def get_groupnames_with_reviewer_role(self):
        return self.get_groupnames_with_role('Reviewer')

    def get_groupnames_with_publisher_role(self):
        return self.get_groupnames_with_role('Publisher')

    def get_groupnames_with_manager_role(self):
        return self.get_groupnames_with_role('Manager')
