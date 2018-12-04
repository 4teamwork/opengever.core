from ftw.builder import builder_registry
from opengever.ogds.models.group import Group
from opengever.ogds.models.team import Team
from opengever.testing.builders.sql import SqlObjectBuilder


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
