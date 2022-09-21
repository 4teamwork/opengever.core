from AccessControl.Permissions import add_user_folders
from opengever.ogds.auth import plugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    registerMultiPlugin(plugin.OGDSAuthenticationPlugin.meta_type)
    context.registerClass(
        plugin.OGDSAuthenticationPlugin,
        permission=add_user_folders,
        constructors=(plugin.manage_addOGDSAuthenticationPlugin,
                      plugin.addOGDSAuthenticationPlugin),
        visibility=None,
    )
