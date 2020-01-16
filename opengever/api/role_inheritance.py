from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.workspace.participation import WORKSPCAE_ADMIN
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides


class RoleInheritanceBase(Service):

    def _serialize_blocked(self):
        return {
            'blocked': self.context.has_blocked_local_role_inheritance()
        }


class RoleInheritanceGet(RoleInheritanceBase):

    def reply(self):
        return self._serialize_blocked()


class RoleInheritancePost(RoleInheritanceBase):

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)
        blocked = data.get('blocked')
        copy_roles = data.get('copy_roles', False)

        if blocked is None:
            raise BadRequest('Must supply blocked in JSON body.')

        if blocked == self.context.has_blocked_local_role_inheritance():
            self.request.response.setStatus(409)
            return self._serialize_blocked()

        if blocked:
            if copy_roles:
                self._copy_assigments_from_parent_with_local_roles()
            else:
                parent_with_local_roles = self.context.get_parent_with_local_roles()
                if WORKSPCAE_ADMIN.id in api.user.get_roles(obj=parent_with_local_roles):
                    # If the current user is a workspace admin, we add it
                    # as the only workspace admin for the context.
                    self._add_current_user_as_admin_to_local_roles()
                else:
                    # It's a manager or someone else without direct permission
                    # to this workpace. We don't want to add this user to the
                    # workspace. So we add all current workspace admins as new
                    # workspace admins.
                    self._add_current_worskspace_admins_to_local_roles()
        else:
            self._delete_local_role_assignments()

        self.context.__ac_local_roles_block__ = blocked
        self.context.reindexObjectSecurity()

        return self._serialize_blocked()

    def _copy_assigments_from_parent_with_local_roles(self):
        parent_with_local_roles = self.context.get_parent_with_local_roles()
        source_manager = RoleAssignmentManager(parent_with_local_roles)
        source_manager.copy_assigments_to(self.context)

    def _delete_local_role_assignments(self):
        RoleAssignmentManager(self.context).clear_all()

    def _add_current_user_as_admin_to_local_roles(self):
        assignment = SharingRoleAssignment(
            api.user.get_current().id,
            [WORKSPCAE_ADMIN.id], self.context)
        RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

    def _add_current_worskspace_admins_to_local_roles(self):
        parent_with_local_roles = self.context.get_parent_with_local_roles()
        roles_manager = RoleAssignmentManager(self.context)

        for principal, roles in parent_with_local_roles.get_local_roles():
            if WORKSPCAE_ADMIN.id in roles:
                assignment = SharingRoleAssignment(principal, roles, self.context)
                roles_manager.add_or_update_assignment(assignment)
