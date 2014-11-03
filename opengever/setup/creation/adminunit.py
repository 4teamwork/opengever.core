from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup.creation.unit import UnitCreator
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from opengever.setup import DEVELOPMENT_SERVER_PORT
from opengever.setup import DEVELOPMENT_SERVER_HOSTNAME
from opengever.setup import DEVELOPMENT_IP_ADDRESS


class AdminUnitCreator(UnitCreator):

    item_name = 'AdminUnit'
    item_class = AdminUnit
    required_attributes = ('unit_id', 'ip_address', 'site_url',
                           'public_url', 'abbreviation')

    def apply_development_config(self, item):
        admin_unit_id = item['unit_id']
        url = 'http://{}:{}/{}'.format(DEVELOPMENT_SERVER_HOSTNAME,
                                       DEVELOPMENT_SERVER_PORT,
                                       admin_unit_id)
        item['site_url'] = url
        item['public_url'] = url
        item['ip_address'] = DEVELOPMENT_IP_ADDRESS

    def create_unit(self, item):
        super(AdminUnitCreator, self).create_unit(item)

        registry = getUtility(IRegistry)
        admin_unit = registry.forInterface(IAdminUnitConfiguration)
        admin_unit.current_unit_id = unicode(item['unit_id'])
