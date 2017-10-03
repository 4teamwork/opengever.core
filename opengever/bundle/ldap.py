from copy import copy
from plone import api
import logging
import transaction


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

originally_enabled_plugins = None

LDAP_PLUGIN_META_TYPES = ('Plone LDAP plugin',
                          'Plone Active Directory plugin')


class DisabledLDAP(object):
    """Context manager that temporarily disables any LDAP PAS plugins.
    """

    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        disable_ldap(self.portal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            # Exception happened, make sure transaction is rolled back
            transaction.abort()
            transaction.begin()

        enable_ldap(self.portal)

        # Make sure persistent changes that re-enable LDAP are committed
        transaction.commit()


def disable_ldap(portal):
    global originally_enabled_plugins

    if originally_enabled_plugins is not None:
        # Nested use of these functions or the context manager isn't supported
        raise Exception("Must re-enable LDAP before disabling it again!")

    originally_enabled_plugins = {}

    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')

    # Save state of enabled plugins in a mapping of the form
    # plugin_type_name -> tuple(plugin_ids)
    for iface, plugin_ids in plugin_registry._plugins.items():
        plugin_type_name = plugin_registry._plugin_type_info[iface]['id']
        originally_enabled_plugins[plugin_type_name] = copy(plugin_ids)

        # Disable LDAP Plugins
        for plugin_id in plugin_ids:
            plugin = uf[plugin_id]
            if plugin.meta_type in LDAP_PLUGIN_META_TYPES:
                plugin_registry.deactivatePlugin(iface, plugin_id)

    log.info('Disabled LDAP plugin(s).')


def enable_ldap(portal):
    global originally_enabled_plugins
    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')

    # Re-enable plugins that got disabled before
    for plugin_type_name, plugin_ids in originally_enabled_plugins.items():
        iface = plugin_registry._getInterfaceFromName(plugin_type_name)
        for plugin_id in plugin_ids:
            if plugin_id not in plugin_registry.listPluginIds(iface):
                plugin_registry.activatePlugin(iface, plugin_id)

    originally_enabled_plugins = None
    log.info('Enabled LDAP plugin(s).')
