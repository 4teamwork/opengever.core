from opengever.base.role_assignments import RoleAssignmentManager
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

        if blocked is None:
            raise BadRequest('Must supply blocked in JSON body.')

        if blocked == self.context.has_blocked_local_role_inheritance():
            self.request.response.setStatus(409)
            return self._serialize_blocked()

        if blocked:
            self._copy_assigments_from_parent_with_local_roles()
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
