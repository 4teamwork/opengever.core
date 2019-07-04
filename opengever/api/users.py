from plone import api
from plone.restapi.services.users.get import UsersGet


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
