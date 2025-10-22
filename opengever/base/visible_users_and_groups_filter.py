from opengever.ogds.models.group_membership import groups_users
from opengever.ogds.models.service import ogds_service
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from sqlalchemy.sql import select
from zope.globalrequest import getRequest


class VisibleUsersAndGroupsFilter:
    """Provides functions to check if a specific user or group should be
    visible to the currently logged in user or not.

    In GEVER user and group information is exposed to all users independant
    of their access rights. In teamraum users are only allowed to get user
    information about users that participate in workspaces the user
    has access to.
    """

    ACCESS_ALL_USERS_AND_GROUPS_PERMISSION = 'opengever.workspace: Access all users and groups'
    ALLOWED_USERS_AND_GROUPS_CACHEKEY = '_visible_users_and_groups_allowed_users_and_groups'

    def is_teamraum(self):
        return is_workspace_feature_enabled()

    def has_all_users_and_groups_permission(self):
        return api.user.has_permission(self.ACCESS_ALL_USERS_AND_GROUPS_PERMISSION)

    def can_access_all_principals(self):
        if not self.is_teamraum():
            return True

        return self.has_all_users_and_groups_permission()

    def can_access_principal(self, principal_id):
        if self.can_access_all_principals():
            return True

        return principal_id in self.get_whitelisted_principals()

    def get_whitelisted_principals(self):
        """This function returns a set of all principals which are
        whitelisted to access for the current user.

        Whitelisted principals are all user and group ids which are participating
        in the same workspaces as the currently logged in user.
        """
        request = getRequest()

        allowed_users_and_groups = getattr(
            request, self.ALLOWED_USERS_AND_GROUPS_CACHEKEY, None)

        if allowed_users_and_groups is None:
            allowed_users_and_groups = self.extract_allowed_users_and_groups()
            allowed_users_and_groups += self.extract_group_members(allowed_users_and_groups)
            allowed_users_and_groups += [api.user.get_current().getId()]
            setattr(request, self.ALLOWED_USERS_AND_GROUPS_CACHEKEY,
                    allowed_users_and_groups)

        return set(allowed_users_and_groups)

    def extract_allowed_users_and_groups(self):
        catalog = api.portal.get_tool('portal_catalog')
        zcatalog = catalog._catalog

        workspace_brains = catalog(portal_type="opengever.workspace.workspace",
                                   hide_member_details=False)
        allowedRolesAndUsers_index = zcatalog.getIndex('allowedRolesAndUsers')
        rids = [zcatalog.uids[brain.getPath()] for brain in workspace_brains]

        allowedRolesAndUsers_facet = set()
        [allowedRolesAndUsers_facet.update(allowedRolesAndUsers_index.getEntryForObject(rid)) for rid in rids]

        return [
            index_value.split('user:')[-1]
            for index_value in allowedRolesAndUsers_facet
            if index_value.startswith('user:')
        ]

    def extract_group_members(self, groupids):
        return [
            userid
            for userid, in ogds_service()
            .session.execute(
                select([groups_users.c.userid], groups_users.c.groupid.in_(groupids))
            )
            .fetchall()
        ]


visible_users_and_groups_filter = VisibleUsersAndGroupsFilter()
