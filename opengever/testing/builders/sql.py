from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from opengever.globalindex.model.task import Task
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class SqlObjectBuilder(object):
    id_argument_name = None
    mapped_class = None

    def __init__(self, session):
        self.session = session
        self.db_session = create_session()
        self.arguments = {}

    def id(self, identifier):
        self.arguments[self.id_argument_name] = identifier
        return self

    def create(self, **kwargs):
        self.before_create()
        obj = self.create_object(**kwargs)
        self.add_object_to_session(obj)
        obj = self.after_create(obj)
        self.commit()
        return obj

    def before_create(self):
        pass

    def after_create(self, obj):
        return obj

    def commit(self):
        if self.session.auto_commit:
            transaction.commit()

    def add_object_to_session(self, obj):
        self.db_session.add(obj)

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def create_object(self):
        return self.mapped_class(**self.arguments)


class AdminUnitBuilder(SqlObjectBuilder):

    mapped_class = AdminUnit
    id_argument_name = 'unit_id'

    def __init__(self, session):
        super(AdminUnitBuilder, self).__init__(session)
        self.arguments['unit_id'] = u'foo'
        self.org_unit = None
        self._as_current_admin_unit = False

    def wrapping_org_unit(self, org_unit):
        self.org_unit = org_unit
        self.arguments.update(dict(
            unit_id=org_unit.id(),
            title=org_unit.label(),
        ))
        return self

    def after_create(self, obj):
        if self.org_unit:
            self.org_unit.assign_to_admin_unit(obj)
        return obj

    def as_current_admin_unit(self):
        self._as_current_admin_unit = True
        return self

    def assign_org_units(self, units):
        clients = [u._client for u in units]
        for client in clients:
            # XXX could be solved better
            self.add_object_to_session(client)
        self.arguments['org_units'] = clients

        return self

    def after_create(self, obj):
        if self._as_current_admin_unit:
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IAdminUnitConfiguration)
            proxy.current_unit_id = self.arguments.get(self.id_argument_name)
        return obj


builder_registry.register('admin_unit', AdminUnitBuilder)


class OrgUnitBuilder(SqlObjectBuilder):

    mapped_class = Client
    id_argument_name = 'client_id'

    def __init__(self, session):
        super(OrgUnitBuilder, self).__init__(session)
        self.arguments['client_id'] = u'rr'
        self._as_current_org_unit = False
        self._with_inbox_group = False
        self._with_users_group = False
        self._inbox_users = set()
        self._group_users = set()

    def before_create(self):
        self._assemble_groups()

    def after_create(self, obj):
        org_unit = OrgUnit(obj)
        if self._as_current_org_unit:
            get_ou_selector().set_current_unit(org_unit.id())
        return org_unit

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
        client_id = self.arguments.get(self.id_argument_name)
        users_group_id = "{}_users".format(client_id)
        users_inbox_id = "{}_inbox_users".format(client_id)

        if self._with_users_group:
            users_group = create(Builder('ogds_group')
                                 .having(groupid=users_group_id,
                                         users=list(self._group_users)))
            self.arguments['users_group'] = users_group

        if self._with_inbox_group:
            inbox_group = create(Builder('ogds_group')
                                 .having(groupid=users_inbox_id,
                                         users=list(self._inbox_users)))
            self.arguments['inbox_group'] = inbox_group

    def as_current_org_unit(self):
        self._as_current_org_unit = True
        return self


builder_registry.register('org_unit', OrgUnitBuilder)


class UserBuilder(SqlObjectBuilder):

    mapped_class = User
    id_argument_name = 'userid'

    def __init__(self, session):
        super(UserBuilder, self).__init__(session)
        self.groups = []
        self.arguments['userid'] = TEST_USER_ID

    def in_group(self, group):
        self.groups.append(group)
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

builder_registry.register('ogds_group', GroupBuilder)


class TaskBuilder(SqlObjectBuilder):

    mapped_class = Task
    id_argument_name = 'task_id'

builder_registry.register('globalindex_task', GroupBuilder)
