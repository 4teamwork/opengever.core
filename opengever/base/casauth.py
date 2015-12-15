from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from urlparse import urljoin


def is_cas_auth_enabled():
    acl_users = api.portal.get_tool('acl_users')
    challenge_plugin = acl_users.plugins.listPlugins(IChallengePlugin)[0]
    return isinstance(challenge_plugin[1], CASAuthenticationPlugin)


def get_cluster_base_url():
    """This function *guesses* the base URL for this GEVER cluster
    (always ending with a trailing slash).

    This is known to be incorrect for deployments with multiple admin units,
    and will be fixed later, once we store the configuration for the
    GEVER cluster in the OGDS.
    """
    base_url = get_current_admin_unit().public_url
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    return base_url


def get_cas_server_url():
    """Get the CAS server URL from the ftw.casauth plugin.
    """
    acl_users = api.portal.get_tool('acl_users')
    cas_auth = acl_users.cas_auth
    url = getattr(cas_auth, 'cas_server_url', None)
    return url


def build_cas_server_url():
    """Build the URL to the CAS server, based on the GEVER cluster URL.

    This URL should only be constructed once during setup, in order to
    initially configure the ftw.casauth plugin.
    """
    base_url = get_cluster_base_url()
    return urljoin(base_url, 'portal')
