from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup.creation.unit import UnitCreator


class AdminUnitCreator(UnitCreator):

    def create_unit(self, item):
        self.session.add(AdminUnit(
            unit_id=item['unit_id'],
            title=item['title'],
            ))
