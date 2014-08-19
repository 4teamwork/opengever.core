from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup.creation.unit import UnitCreator


class AdminUnitCreator(UnitCreator):

    item_name = 'AdminUnit'
    item_class = AdminUnit
    required_attributes = ('unit_id',)
