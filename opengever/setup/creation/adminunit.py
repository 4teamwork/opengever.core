from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup import DEVELOPMENT_IP_ADDRESS
from opengever.setup import DEVELOPMENT_SERVER_HOSTNAME
from opengever.setup import DEVELOPMENT_SERVER_PORT
from opengever.setup.creation.unit import UnitCreator


class AdminUnitCreator(UnitCreator):

    item_name = 'AdminUnit'
    item_class = AdminUnit
    required_attributes = ('unit_id', 'ip_address', 'site_url',
                           'public_url', 'abbreviation')

    def apply_development_config(self, item):
        if self.is_policyless:
            plone_site_id = 'gever'
        else:
            plone_site_id = item['unit_id']

        url = 'http://{}:{}/{}'.format(DEVELOPMENT_SERVER_HOSTNAME,
                                       DEVELOPMENT_SERVER_PORT,
                                       plone_site_id)
        item['site_url'] = url
        item['public_url'] = url
        item['ip_address'] = DEVELOPMENT_IP_ADDRESS
