from ftw.builder import builder_registry
from opengever.ogds.models.group import Group
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.testing.builders.sql import SqlObjectBuilder


class UserBuilder(SqlObjectBuilder):

    mapped_class = User
    id_argument_name = 'userid'

    def __init__(self, session):
        super(UserBuilder, self).__init__(session)
        self.groups = []
        self.arguments['userid'] = 'test'
        self.arguments['email'] = 'test@example.org'

    def in_group(self, group):
        if group and group not in self.groups:
            self.groups.append(group)
        return self

    def assign_to_org_units(self, org_units):
        for org_unit in org_units:
            self.groups.append(org_unit.users_group)
        return self

    def create_object(self):
        obj = super(UserBuilder, self).create_object()
        if self.groups:
            obj.groups.extend(self.groups)
        return obj


builder_registry.register('ogds_user', UserBuilder)


class GroupBuilder(SqlObjectBuilder):

    mapped_class = Group
    id_argument_name = 'groupid'

    def __init__(self, session):
        super(GroupBuilder, self).__init__(session)
        self.arguments['groupid'] = 'testgroup'
        self.arguments['title'] = 'Test Group'


builder_registry.register('ogds_group', GroupBuilder)


class TeamBuilder(SqlObjectBuilder):

    mapped_class = Team
    id_argument_name = 'team_id'


builder_registry.register('ogds_team', TeamBuilder)
