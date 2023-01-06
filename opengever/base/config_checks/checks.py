from opengever.base.interfaces import IConfigCheck
from opengever.bundle.ldap import LDAP_PLUGIN_META_TYPES
from plone import api
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class BaseCheck(object):
    def __init__(self, context):
        self.context = context

    @property
    def check_id(self):
        return self.__class__.__name__

    def config_error(self, title, description=''):
        return {
            'id': self.check_id,
            'title': title,
            'description': description,
        }


@implementer(IConfigCheck)
@adapter(Interface)
class LDAPPluginOrderCheck(BaseCheck):

    def check(self):
        is_first_entry = True
        for plugin_id, plugin in self.get_plugins():
            if plugin.meta_type in LDAP_PLUGIN_META_TYPES and not is_first_entry:
                return self.config_error(
                    title='LDAP authentication plugin with the ID: "{}" is not at the '
                          'first position'.format(plugin_id),
                    description='Move the active ldap plugin from '
                                '/acl_users/plugins/manage_plugins > "Authentication Plugins" '
                                'to the first position. This is required to properly lookup '
                                'user metadata from the ldap.')

            is_first_entry = False

    def get_plugins(self):
        return api.portal.get_tool('acl_users').plugins.listPlugins(IAuthenticationPlugin)
