from plone import api
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


original_plugins = None


def disable_ldap(portal):
    ldap_plugins = []
    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')
    for plugin in uf.objectValues():
        if plugin.meta_type in ['Plone LDAP plugin',
                                'Plone Active Directory plugin']:
            ldap_plugins.append(plugin.getId())

    global original_plugins
    original_plugins = plugin_registry._plugins
    plugins_without_ldap = {}
    for interface, plugins in original_plugins.items():
        actives = tuple([p for p in plugins if p not in ldap_plugins])
        plugins_without_ldap[interface] = actives

    plugin_registry._plugins = plugins_without_ldap
    log.info('Disabled LDAP plugin.')


def enable_ldap(portal):
    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')
    plugin_registry._plugins = original_plugins
    log.info('Enabled LDAP plugin.')
