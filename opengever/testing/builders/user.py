from ftw.builder import builder_registry
from ftw.builder.user import UserBuilder as OriginalUserBuilder
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin


class UserBuilder(OriginalUserBuilder):

    def create_user(self, userid, password, roles, properties):
        plugin_registry = self.portal.acl_users._getOb('plugins')

        originally_active = 'source_users' in plugin_registry._plugins[IUserEnumerationPlugin]
        if not originally_active:
            # Temporarily activate user enumeration for source_users
            # Otherwise the registration tool fail fail to fetch the member it just
            # added during user creation.
            plugin_registry.activatePlugin(IUserEnumerationPlugin, 'source_users')

        member = super(UserBuilder, self).create_user(userid, password, roles, properties)

        if not originally_active:
            # Disable user enumeration for source_users again
            plugin_registry.deactivatePlugin(IUserEnumerationPlugin, 'source_users')

        return member


del builder_registry.builders['user']
builder_registry.register('user', UserBuilder)
