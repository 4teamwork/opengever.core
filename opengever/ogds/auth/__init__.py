from AccessControl.Permissions import add_user_folders
from opengever.ogds.auth import admin_unit
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

    registerMultiPlugin(admin_unit.AdminUnitAuthenticationPlugin.meta_type)
    context.registerClass(
        admin_unit.AdminUnitAuthenticationPlugin,
        permission=add_user_folders,
        constructors=(admin_unit.manage_addAdminUnitAuthenticationPlugin,
                      admin_unit.addAdminUnitAuthenticationPlugin),
        visibility=None,
    )
