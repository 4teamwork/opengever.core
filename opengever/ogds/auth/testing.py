from copy import copy
from opengever.ogds.auth.plugin import OGDSAuthenticationPlugin
from opengever.testing import IntegrationTestCase


class DisabledPluginTypes(object):
    """Context manager to temporarily deactivate certain PAS plugin types.

    Needed in order to write test that demonstrate that our OGDS auth plugin
    could substitute their functionality.
    """

    types_to_disable = None

    def __init__(self, acl_users):
        if self.types_to_disable is None:
            raise NotImplementedError(
                'Subclasses must define `types_to_disable`')

        self.acl_users = acl_users
        self._been_disabled = False
        self._originally_enabled = {}

    def __enter__(self):
        if self._been_disabled:
            raise AssertionError('Already disabled')

        # Back up originally enabled capability interfaces for plugins
        plugin_registry = self.acl_users._getOb('plugins')
        for iface, plugin_ids in plugin_registry._plugins.items():
            plugin_type_name = plugin_registry._plugin_type_info[iface]['id']
            if plugin_type_name in self.types_to_disable:
                self._originally_enabled[plugin_type_name] = copy(plugin_ids)

                # Disable plugins
                for plugin_id in plugin_ids:
                    plugin_registry.deactivatePlugin(iface, plugin_id)

        self._been_disabled = True
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if not self._been_disabled:
            raise AssertionError('Already (re)enabled')

        plugin_registry = self.acl_users._getOb('plugins')

        # Re-enable plugins that got disabled before
        for plugin_type_name, plugin_ids in self._originally_enabled.items():
            iface = plugin_registry._getInterfaceFromName(plugin_type_name)
            for plugin_id in plugin_ids:
                if plugin_id not in plugin_registry.listPluginIds(iface):
                    plugin_registry.activatePlugin(iface, plugin_id)

        self._been_disabled = False
        return False


class DisabledUserPlugins(DisabledPluginTypes):

    types_to_disable = [
        'IUserEnumerationPlugin',
    ]


class DisabledGroupPlugins(DisabledPluginTypes):

    types_to_disable = [
        'IGroupsPlugin',
    ]


class OGDSAuthTestCase(IntegrationTestCase):

    def setUp(self):
        super(OGDSAuthTestCase, self).setUp()
        self.disabled_user_plugins = DisabledUserPlugins(self.uf)
        self.disabled_group_plugins = DisabledGroupPlugins(self.uf)

    @property
    def uf(self):
        return self.portal.acl_users

    def install_ogds_plugin(self):
        plugin = OGDSAuthenticationPlugin('ogds_auth')
        self.uf._setObject(plugin.getId(), plugin)
        plugin = self.uf['ogds_auth']
        plugin.manage_activateInterfaces([
            'IUserEnumerationPlugin',
            'IGroupsPlugin',
        ])
        self.plugin = plugin

    def uninstall_ogds_plugin(self):
        if getattr(self, 'plugin', None):
            del self.plugin
            del self.uf['ogds_auth']
