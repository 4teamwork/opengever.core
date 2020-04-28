from opengever.base.interfaces import IOpengeverBaseLayer
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.user import BaseSerializer
from plone.restapi.services.users.get import UsersGet
from Products.CMFCore.interfaces._tools import IMemberData
from zope.component import adapter
from zope.interface import implementer


class GeverUsersGet(UsersGet):
    """Customize permissions to enumarate and query user information.

    By default its protected with `manage portal` permission, but in GEVER all
    users should be able to enumarate, query or access user information for
    all.
    """

    def _has_allowed_role(self):
        # We're not able to check for the `View` permission, because also
        # anonymous users have the `View` permissions (login form).
        current_roles = api.user.get_roles()
        for role in ['Member', 'Reader', 'Manager']:
            if role in current_roles:
                return True
        return False

    def has_permission_to_query(self):
        return self._has_allowed_role()

    def has_permission_to_enumerate(self):
        return self._has_allowed_role()


@implementer(ISerializeToJson)
@adapter(IMemberData, IOpengeverBaseLayer)
class SerializeUserToJson(BaseSerializer):

    def __call__(self):
        data = super(SerializeUserToJson, self).__call__()
        catalog = api.portal.get_tool('portal_catalog')
        roles_and_principals = catalog._listAllowedRolesAndUsers(self.context.getUser())
        roles_and_principals = [principal.replace('user:', 'principal:')
                                for principal in roles_and_principals]
        data['roles_and_principals'] = roles_and_principals
        return data
