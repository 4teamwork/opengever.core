from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin


CAS_SERVER_URL_FORMAT = '{admin_unit_public_url}/portal'
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
        cas_server_url = CAS_SERVER_URL_FORMAT.format(
            admin_unit_public_url=get_current_admin_unit().public_url)
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


def rename_session_cookie(site):
    # Rename session cookie and increase validity timeout to 24h
    plugin = api.portal.get_tool('acl_users')['session']
    plugin.manage_changeProperties({
        'cookie_name': '__ac_' + site.getId().replace('-', '_'),
        'timeout': SESSION_DEFAULT_TIMEOUT,
    })
