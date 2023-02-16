from ftw.upgrade import UpgradeStep
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin


class FixOrderOfIPropertiesPluginPASPlugins(UpgradeStep):
    """Fix order of IPropertiesPlugin PAS plugins.
    """

    def __call__(self):
        acl_users = api.portal.get_tool('acl_users')
        plugins = acl_users.plugins

        if 'ldap' in plugins.listPluginIds(IPropertiesPlugin):
            plugins.movePluginsTop(IPropertiesPlugin, ('ldap',))
