from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from urlparse import urljoin
import re


def is_cas_auth_enabled():
    acl_users = api.portal.get_tool('acl_users')
    challenge_plugin = acl_users.plugins.listPlugins(IChallengePlugin)[0]
    return isinstance(challenge_plugin[1], CASAuthenticationPlugin)


def get_cluster_base_url():
    """Determine the base URL for this GEVER cluster (always ending with a
    trailing slash).
    """
    admin_unit = get_current_admin_unit()

    base_url = admin_unit.public_url
    if not base_url.endswith('/'):
        base_url = base_url + '/'

    # XXX: Heuristic in order to determine the correct cluster base URL:
    # If URL ends with the ID of the current admin unit, we're probably
    # dealing with a deployment with multiple admin units. So we strip the
    # admin unit ID from the end of the URL to get the correct cluster base.
    #
    # This heuristic will later be replaced with a configuration of the
    # cluster base URL in OGDS.
    unit_suffix_pattern = re.compile('/{}/$'.format(admin_unit.unit_id))
    base_url = re.sub(unit_suffix_pattern, '/', base_url)

    return base_url


def get_gever_portal_url():
    """Get the URL of the GEVER portal.
    """
    base_url = get_cluster_base_url()
    return urljoin(base_url, 'portal')


def get_cas_server_url():
    """Get the CAS server URL from the ftw.casauth plugin.
    """
    acl_users = api.portal.get_tool('acl_users')
    if 'cas_auth' not in acl_users:
        return None
    cas_auth = acl_users.cas_auth
    url = getattr(cas_auth, 'cas_server_url', None)
    return url


def build_cas_server_url(cas_path):
    """Build the URL to the CAS server, based on the GEVER cluster URL.

    This URL should only be constructed once during setup, in order to
    initially configure the ftw.casauth plugin.
    """
    base_url = get_cluster_base_url()
    return urljoin(base_url, cas_path)
