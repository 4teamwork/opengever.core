from opengever.ogds.models.client import Client
from opengever.setup.creation.unit import UnitCreator


class OrgUnitCreator(UnitCreator):

    def create_unit(self, item):
        self.session.add(Client(
            client_id=item['unit_id'],
            title=item['title'],
            admin_unit_id=item['admin_unit_id']
            ))
