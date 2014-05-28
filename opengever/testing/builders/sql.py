from ftw.builder import builder_registry
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
import transaction


class SqlObjectBuilder(object):

    mapped_class = None

    def __init__(self, session):
        self.session = session
        self.db_session = create_session()
        self.arguments = {}

    def create(self, **kwargs):
        self.before_create()
        obj = self.create_object(**kwargs)
        self.after_create(obj)
        return obj

    def before_create(self):
        pass

    def after_create(self, obj):
        if self.session.auto_commit:
            transaction.commit()

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def create_object(self):
        obj = self._create_mapped_class()
        self.db_session.add(obj)
        return obj

    def _create_mapped_class(self):
        return self.mapped_class(**self.arguments)


class AdminUnitBuilder(SqlObjectBuilder):

    mapped_class = AdminUnit

    def __init__(self, session):
        super(AdminUnitBuilder, self).__init__(session)
        self.arguments['unit_id'] = 'foo'
        self.org_unit = None

    def wrapping_org_unit(self, org_unit):
        self.org_unit = org_unit
        self.arguments.update(dict(
            unit_id=org_unit.id(),
            title=org_unit.label(),
        ))
        return self

    def create_object(self):
        obj = super(AdminUnitBuilder, self).create_object()
        if self.org_unit:
            self.org_unit.assign_to_admin_unit(obj)
        return obj

builder_registry.register('admin_unit', AdminUnitBuilder)


class OrgUnitBuilder(SqlObjectBuilder):

    mapped_class = Client

    def create(self, **kwargs):
        instance = super(OrgUnitBuilder, self).create(**kwargs)
        return OrgUnit(instance)

builder_registry.register('org_unit', OrgUnitBuilder)


class UserBuilder(SqlObjectBuilder):

    mapped_class = User

    def __init__(self, session):
        super(UserBuilder, self).__init__(session)
        self.groups = []
        self.arguments['userid'] = 'peter'

    def in_group(self, group):
        self.groups.append(group)
        return self

    def _create_mapped_class(self):
        obj = self.mapped_class(self.arguments.pop('userid'),
                                **self.arguments)
        if self.groups:
            obj.groups.extend(self.groups)
        return obj

builder_registry.register('ogds_user', UserBuilder)


class GroupBuilder(SqlObjectBuilder):

    mapped_class = Group

    def __init__(self, session):
        super(GroupBuilder, self).__init__(session)
        self.arguments['groupid'] = 'testgroup'

    def _create_mapped_class(self):
        return self.mapped_class(self.arguments.pop('groupid'),
                                 **self.arguments)


builder_registry.register('ogds_group', GroupBuilder)
