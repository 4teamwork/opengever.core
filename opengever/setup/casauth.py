from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.base.casauth import build_cas_server_url
from plone import api


SESSION_DEFAULT_TIMEOUT = 24 * 60 * 60


def setup_cas(site):
    """Install and configure CAS authentication plugin.
       Rename session cookie to avoid conflicts with multiple clients.
    """
    install_cas_auth_plugin()
    rename_session_cookie(site)


def install_cas_auth_plugin():
    acl_users = api.portal.get_tool('acl_users')

    if 'cas_auth' not in acl_users.objectIds():
        # Build the URL for the CAS server once during initial setup and
        # configure it for the plugin.
        cas_server_url = build_cas_server_url()

        plugin = CASAuthenticationPlugin(
            'cas_auth', cas_server_url=cas_server_url)
        acl_users._setObject(plugin.getId(), plugin)
        plugin = acl_users['cas_auth']
        plugin.manage_activateInterfaces([
            'IAuthenticationPlugin',
            'IChallengePlugin',
            'IExtractionPlugin',
        ])

        # Move challenge plugin to top position
        while not acl_users.plugins.listPluginIds(IChallengePlugin)[0] == 'cas_auth':
            acl_users.plugins.movePluginsUp(IChallengePlugin, ['cas_auth'])

    # Deactivate LDAP authentication
    auth_plugins = acl_users.plugins.listPlugins(IAuthenticationPlugin)
    for plugin_id, plugin in auth_plugins:
        if ILDAPMultiPlugin.providedBy(plugin):
            acl_users.plugins.deactivatePlugin(
                IAuthenticationPlugin, plugin_id)


def rename_session_cookie(site):
    # Rename session cookie and increase validity timeout to 24h
    plugin = api.portal.get_tool('acl_users')['session']
    plugin.manage_changeProperties({
        'cookie_name': '__ac_' + site.getId().replace('-', '_'),
        'timeout': SESSION_DEFAULT_TIMEOUT,
    })
