from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.client import Client
from opengever.setup.creation.unit import UnitCreator
from opengever.setup.exception import GeverSetupException


class OrgUnitCreator(UnitCreator):

    item_name = 'OrgUnit'
    item_class = Client
    required_attributes = ('client_id', 'admin_unit_id')

    def check_constraints(self, item):
        super(OrgUnitCreator, self).check_constraints(item)

        admin_unit_id = item['admin_unit_id']
        admin_unit = ogds_service().fetch_admin_unit(admin_unit_id)
        if admin_unit is None:
            raise GeverSetupException(
                "Missing Admin-Unit {}".format(admin_unit_id))
