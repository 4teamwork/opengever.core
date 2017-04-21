from persistent.mapping import PersistentMapping
from plone import api
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


original_plugins = None


class DisabledLDAP(object):
    """Context manager that temporarily disables any LDAP PAS plugins.
    """

    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        disable_ldap(self.portal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        enable_ldap(self.portal)


def disable_ldap(portal):
    global original_plugins

    if original_plugins is not None:
        # Nested use of these functions or the context manager isn't supported
        raise Exception("Must re-enable LDAP before disabling it again!")

    ldap_plugins = []
    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')
    for plugin in uf.objectValues():
        if plugin.meta_type in ['Plone LDAP plugin',
                                'Plone Active Directory plugin']:
            ldap_plugins.append(plugin.getId())

    original_plugins = plugin_registry._plugins
    plugins_without_ldap = PersistentMapping()
    for interface, plugins in original_plugins.items():
        actives = tuple([p for p in plugins if p not in ldap_plugins])
        plugins_without_ldap[interface] = actives

    plugin_registry._plugins = plugins_without_ldap
    log.info('Disabled LDAP plugin.')


def enable_ldap(portal):
    global original_plugins
    uf = api.portal.get_tool('acl_users')
    plugin_registry = uf._getOb('plugins')
    plugin_registry._plugins = original_plugins
    original_plugins = None
    log.info('Enabled LDAP plugin.')
