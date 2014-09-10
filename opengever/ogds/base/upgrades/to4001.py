from ftw.upgrade import UpgradeStep
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


ID_FIELD = 'opengever.ogds.base.interfaces.IClientConfiguration.client_id'


class CreateAdminUnitRegistry(UpgradeStep):

    def __call__(self):
        """Migrate ogds db. Adds the admin_units table
        and according relationship-field."""

        self.setup_install_profile(
            'profile-opengever.ogds.base.upgrades:4001')

        registry = getUtility(IRegistry)
        client_id = registry.get(ID_FIELD, None)
        if client_id is None:
            return

        admin_unit = registry.forInterface(IAdminUnitConfiguration)
        admin_unit.current_unit_id = client_id
