from ftw.upgrade import UpgradeStep
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class CreateAdminUnitRegistry(UpgradeStep):

    def __call__(self):
        """Migrate ogds db. Adds the admin_units table
        and according relationship-field."""

        self.setup_install_profile(
            'profile-opengever.ogds.base.upgrades:3302')

        registry = getUtility(IRegistry)
        client = registry.forInterface(IClientConfiguration)
        admin_unit = registry.forInterface(IAdminUnitConfiguration)
        admin_unit.current_unit_id = client.client_id
