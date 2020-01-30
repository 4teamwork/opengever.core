from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.sharing.browser.sharing import ROLES_ORDER
from opengever.sharing.security import disabled_permission_check
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.sharing import SharingGet as APISharingGet
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class SharingGet(APISharingGet):
    """plone.restapi sharing endpoint customization:

    Disable `plone.DelegateRoles` permission check, all users should be
    able to access sharing informations.

    Add additional request parameter `ignore_permissions`, which is used for
    readonly listings of the current local roles, as it's done in the sharing
    tab.
    """

    def reply(self):
        """Disable `plone.DelegateRoles` permission check.
        """

        serializer = queryMultiAdapter((self.context, self.request),
                                       interface=ISerializeToJson,
                                       name='local_roles')

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        if self.request.form.get('ignore_permissions'):
            with disabled_permission_check():
                data = serializer(search=self.request.form.get('search'))
        else:
            data = serializer(search=self.request.form.get('search'))

        # sort available roles
        data['available_roles'].sort(
            lambda a, b: cmp(ROLES_ORDER.index(a['id']),
                             ROLES_ORDER.index(b['id'])))

        return data


class RoleAssignmentsGet(APISharingGet):
    """API Endpoint which returns a list of all role assignments of
    the current context for a particular user.
    Sharing assignments are skipped.

    GET /@role-assignments/principal_id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RoleAssignmentsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@role-assignments as parameters
        self.params.append(name)
        return self

    def reply(self):
        principal_id = self.read_params()

        manager = RoleAssignmentManager(self.context)
        assignments = manager.get_assignments_by_principal_id(principal_id)

        return [assignment.serialize() for assignment in assignments
                if assignment.cause != ASSIGNMENT_VIA_SHARING]

    def read_params(self):
        """Returns principal_id passed in via traversal parameters.
        """
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply principal ID as URL path parameter.")

        return self.params[0]
