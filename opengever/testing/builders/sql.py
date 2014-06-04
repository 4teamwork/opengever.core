from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
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

    # XXX create this method for every builder
    def id(self, identifier):
        self.arguments[self.id_argument_name] = identifier
        return self

    def create(self, **kwargs):
        self.before_create()
        obj = self.create_object(**kwargs)
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

    def create_object(self):
        obj = super(AdminUnitBuilder, self).create_object()
        if self.org_unit:
            self.org_unit.assign_to_admin_unit(obj)
        return obj

    def as_current_admin_unit(self):
        self._as_current_admin_unit = True
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

    def _create_mapped_class(self):
        return self.mapped_class(self.arguments.pop(self.id_argument_name),
                                 **self.arguments)

    def after_create(self, obj):
        org_unit = OrgUnit(obj)
        if self._as_current_org_unit:
            get_ou_selector().set_current_unit(org_unit.id())
        return org_unit

    def assign_users(self, *users):
        group = create(Builder('ogds_group')
                       .having(groupid=self.arguments.get(self.id_argument_name),
                               users=list(users)))
        self.arguments['users_group'] = group
        return self

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

    def _create_mapped_class(self):
        obj = self.mapped_class(self.arguments.pop(self.id_argument_name),
                                **self.arguments)
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

    def _create_mapped_class(self):
        return self.mapped_class(self.arguments.pop(self.id_argument_name),
                                 **self.arguments)


builder_registry.register('ogds_group', GroupBuilder)
