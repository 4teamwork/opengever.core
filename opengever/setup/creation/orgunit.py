from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.service import ogds_service
from opengever.setup import DEVELOPMENT_USERS_GROUP
from opengever.setup.creation import OGDS_GROUP_KEY_REPLACE_MARKER_PREFIX
from opengever.setup.creation.unit import UnitCreator
from opengever.setup.exception import GeverSetupException
from plone import api
import uuid


class OrgUnitCreator(UnitCreator):

    item_name = 'OrgUnit'
    item_class = OrgUnit
    required_attributes = ('unit_id',
                           'admin_unit_id',
                           'users_group_id',
                           'inbox_group_id')

    def apply_development_config(self, item):
        item['users_group_name'] = DEVELOPMENT_USERS_GROUP
        item['inbox_group_name'] = DEVELOPMENT_USERS_GROUP

    def preprocess(self, item):
        users_group_name = item.get('users_group_name')
        inbox_group_name = item.get('inbox_group_name')
        if users_group_name:
            item['users_group_id'] = self.get_or_create_group_by_name(users_group_name).groupid
            del item['users_group_name']
        if inbox_group_name:
            item['inbox_group_id'] = self.get_or_create_group_by_name(inbox_group_name).groupid
            del item['inbox_group_name']

    def check_constraints(self, item):
        super(OrgUnitCreator, self).check_constraints(item)

        org_unit_id = item['unit_id']
        admin_unit_id = item['admin_unit_id']

        self.check_admin_unit_id(admin_unit_id, org_unit_id)
        self.check_group_id(item['users_group_id'], org_unit_id)
        self.check_group_id(item['inbox_group_id'], org_unit_id)

    def check_admin_unit_id(self, admin_unit_id, org_unit_id):
        admin_unit = ogds_service().fetch_admin_unit(admin_unit_id)
        if admin_unit is None:
            raise GeverSetupException(
                "Missing Admin-Unit '{}' while creating Org-Unit '{}'".format(
                    admin_unit_id, org_unit_id))

    def check_group_id(self, groupid, org_unit_id):
        group = ogds_service().fetch_group(groupid)
        if group is None:
            raise GeverSetupException(
                "Missing Group with groupid '{}' while creating Org-Unit '{}'".format(
                    groupid, org_unit_id))

    def create_unit(self, item):
        super(OrgUnitCreator, self).create_unit(item)

        site = api.portal.get()
        site.acl_users.portal_role_manager.assignRoleToPrincipal(
            'Member', item['users_group_id'])

    def get_or_create_group_by_name(self, group_name):
        group = Group.query.filter(Group.groupname == group_name).one_or_none()
        if not group:
            external_id = OGDS_GROUP_KEY_REPLACE_MARKER_PREFIX + group_name
            group = Group(**{'groupid': uuid.uuid4().hex, 'groupname': group_name, 'external_id': external_id})
            self.session.add(group)

        return group
