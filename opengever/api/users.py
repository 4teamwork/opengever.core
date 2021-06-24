from opengever.base.interfaces import IOpengeverBaseLayer
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.user import BaseSerializer
from plone.restapi.services.users.get import UsersGet
from plone.restapi.services.users.update import UsersPatch
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


class GeverUsersPatch(UsersPatch):
    """Extends the endpoint with the possibility to delete a profile image.
    """

    def reply(self):
        self.maybe_delete_personal_portrait()
        return super(GeverUsersPatch, self).reply()

    def maybe_delete_personal_portrait(self):
        """Deletes the personal portrait if the body contains a 'portrait' with
        the value of 'None'.
        """
        data = json_body(self.request)
        portrait = data.get('portrait')

        # The super method will then take care of the error handling for
        # unauthorized access
        if not (self.can_manage_users or self._get_current_user == self._get_user_id):
            return

        if 'portrait' in data and portrait is None:
            user = self._get_user(self._get_user_id)
            portal_membership = api.portal.get_tool('portal_membership')
            safe_id = portal_membership._getSafeMemberId(user.getId())
            portal_membership.deletePersonalPortrait(str(safe_id))


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
