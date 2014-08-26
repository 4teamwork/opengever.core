from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.org_unit import OrgUnit
from opengever.setup.creation.unit import UnitCreator
from opengever.setup.exception import GeverSetupException


class OrgUnitCreator(UnitCreator):

    item_name = 'OrgUnit'
    item_class = OrgUnit
    required_attributes = ('unit_id',
                           'admin_unit_id',
                           'users_group_id',
                           'inbox_group_id')

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
                "Missing Admin-Unit '{}'' while creating Org-Unit '{}'".format(
                    admin_unit_id, org_unit_id))

    def check_group_id(self, groupid, org_unit_id):
        group = ogds_service().fetch_group(groupid)
        if group is None:
            raise GeverSetupException(
                "Missing Group '{}'' while creating Org-Unit '{}'".format(
                    groupid, org_unit_id))
