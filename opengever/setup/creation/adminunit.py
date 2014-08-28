from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.setup.creation.unit import UnitCreator
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class AdminUnitCreator(UnitCreator):

    item_name = 'AdminUnit'
    item_class = AdminUnit
    required_attributes = ('unit_id', 'ip_address', 'site_url', 'public_url')

    def create_unit(self, item):
        super(AdminUnitCreator, self).create_unit(item)

        registry = getUtility(IRegistry)
        admin_unit = registry.forInterface(IAdminUnitConfiguration)
        admin_unit.current_unit_id = unicode(item['unit_id'])
