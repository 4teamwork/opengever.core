from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from ftw.upgrade import UpgradeStep


class DisableLDAPAuthentication(UpgradeStep):
    """Disable ldap authentication if CAS plugin is activated.
    """

    def __call__(self):
        uf = self.getToolByName('acl_users')
        auth_plugins = uf.plugins.listPluginIds(IAuthenticationPlugin)
        if 'cas_auth' in auth_plugins:
            for plugin_id in auth_plugins:
                plugin = uf[plugin_id]
                if ILDAPMultiPlugin.providedBy(plugin):
                    uf.plugins.deactivatePlugin(
                        IAuthenticationPlugin, plugin_id)
