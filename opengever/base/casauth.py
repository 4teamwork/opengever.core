from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin


CAS_SERVER_URL_FORMAT = '{admin_unit_public_url}/portal'


def is_cas_auth_enabled():
    acl_users = api.portal.get_tool('acl_users')
    challenge_plugin = acl_users.plugins.listPlugins(IChallengePlugin)[0]
    return isinstance(challenge_plugin[1], CASAuthenticationPlugin)


def get_cas_portal_url():
    return CAS_SERVER_URL_FORMAT.format(
        admin_unit_public_url=get_current_admin_unit().public_url.rstrip('/'))
