from ftw.upgrade import UpgradeStep
from opengever.ogds.auth.admin_unit import addAdminUnitAuthenticationPlugin
from plone import api


class AddAdminUnitAuthPlugin(UpgradeStep):
    """Add admin unit auth plugin.
    """

    def __call__(self):
        acl_users = api.portal.get_tool('acl_users')
        if 'octopus_tentacle_plugin' in acl_users:
            acl_users._delObject('octopus_tentacle_plugin')

        addAdminUnitAuthenticationPlugin(
            None, 'admin_unit_auth', 'Admin Unit Authentication Plugin')
