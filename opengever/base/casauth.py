from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin


CAS_SERVER_URL_FORMAT = '{admin_unit_public_url}/portal'


def is_cas_auth_enabled():
    acl_users = api.portal.get_tool('acl_users')
    challenge_plugin = acl_users.plugins.listPlugins(IChallengePlugin)[0]
    return isinstance(challenge_plugin[1], CASAuthenticationPlugin)


def build_cas_portal_url():
    """This function *guesses* the URL for the CAS server, in order to
    initially configure the ftw.casauth plugin during setup.

    This is known to be incorrect for deployments with multiple admin units,
    and will be fixed later, once we store the configuration for the
    GEVER cluster in the OGDS.
    """
    return CAS_SERVER_URL_FORMAT.format(
        admin_unit_public_url=get_current_admin_unit().public_url.rstrip('/'))


def get_cas_portal_url():
    """Get the CAS server URL from the ftw.casauth plugin.
    """
    acl_users = api.portal.get_tool('acl_users')
    cas_auth = acl_users.cas_auth
    url = getattr(cas_auth, 'cas_server_url', None)
    return url
