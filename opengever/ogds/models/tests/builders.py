from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.testing.builders.sql import SqlObjectBuilder


class AdminUnitBuilder(SqlObjectBuilder):

    mapped_class = AdminUnit
    id_argument_name = 'unit_id'

    def __init__(self, session):
        super(AdminUnitBuilder, self).__init__(session)
        self._as_current_admin_unit = False
        self.arguments[self.id_argument_name] = u'foo'
        self.arguments['ip_address'] = '1.2.3.4'
        self.arguments['site_url'] = 'http://example.com'
        self.arguments['public_url'] = 'http://example.com/public'
        self.arguments['abbreviation'] = 'Client1'
        self.org_unit = None

    def wrapping_org_unit(self, org_unit):
        self.org_unit = org_unit
        self.arguments.update(dict(
            unit_id=org_unit.id(),
            title=org_unit.label(),
        ))
        return self

    def as_current_admin_unit(self):
        self._as_current_admin_unit = True
        return self

    def assign_org_units(self, units):
        self.arguments['org_units'] = units
        return self

    def after_create(self, obj):
        if self.org_unit:
            self.org_unit.assign_to_admin_unit(obj)
        return obj


builder_registry.register('admin_unit', AdminUnitBuilder)


class OrgUnitBuilder(SqlObjectBuilder):

    mapped_class = OrgUnit
    id_argument_name = 'unit_id'

    def __init__(self, session):
        super(OrgUnitBuilder, self).__init__(session)
        self.arguments[self.id_argument_name] = u'rr'
        self.arguments['users_group_id'] = 'foo'
        self.arguments['inbox_group_id'] = 'bar'
        self._with_inbox_group = False
        self._with_users_group = False
        self._inbox_users = set()
        self._group_users = set()

    def before_create(self):
        self._assemble_groups()

    def with_default_groups(self):
        self.with_inbox_group()
        self.with_users_group()
        return self

    def with_inbox_group(self):
        self._with_inbox_group = True
        return self

    def with_users_group(self):
        self._with_users_group = True
        return self

    def assign_users(self, users, to_users=True, to_inbox=True):
        if to_users:
            self.with_users_group()
            self._group_users.update(users)

        if to_inbox:
            self.with_inbox_group()
            self._inbox_users.update(users)
        return self

    def _assemble_groups(self):
        if self._with_users_group or self._with_inbox_group:
            unit_id = self.arguments.get(self.id_argument_name)

        if self._with_users_group:
            users_group_id = "{0}_users".format(unit_id)
            users_group_title = '{0} Users Group'.format(unit_id)
            self._create_users_group(users_group_id, users_group_title)

        if self._with_inbox_group:
            users_inbox_id = "{0}_inbox_users".format(unit_id)
            users_inbox_title = '{0} Inbox Users Group'.format(unit_id)
            self._create_inbox_group(users_inbox_id, users_inbox_title)

    def _create_users_group(self, users_group_id, users_group_title=None):
        users_group = create(Builder('ogds_group')
                             .having(groupid=users_group_id,
                                     title=users_group_title,
                                     users=list(self._group_users)))
        self.arguments['users_group'] = users_group

    def _create_inbox_group(self, users_inbox_id, users_inbox_title=None):
        inbox_group = create(Builder('ogds_group')
                             .having(groupid=users_inbox_id,
                                     title=users_inbox_title,
                                     users=list(self._inbox_users)))
        self.arguments['inbox_group'] = inbox_group


builder_registry.register('org_unit', OrgUnitBuilder)


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
