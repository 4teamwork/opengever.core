from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ParticipationTraverseService(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ParticipationTraverseService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self

    def prepare_response_item(self, participant):
        userid = participant.get('token')
        role = PARTICIPATION_ROLES.get(participant.get('roles')[0])
        member = api.user.get(userid=userid)
        return {
            '@id': '{}/@participations/{}'.format(
                self.context.get_context_with_local_roles().absolute_url(), userid),
            '@type': 'virtual.participations.user',
            'participant_fullname': participant.get('name'),
            'is_editable': participant.get('can_manage'),
            'role': {
                'token': role.id,
                'title': role.translated_title(self.request),
            },
            'token': userid,
            'participant_email': member.getProperty('email'),
        }

    def participants(self, context):
        manager = ManageParticipants(context, self.request)
        return manager.get_participants()

    def find_participant(self, token, context):
        for item in self.participants(context):
            if item.get('token') == token:
                return item


class ParticipationsGet(ParticipationTraverseService):
    """API Endpoint which returns a list of all participants for the current
    workspace.

    GET workspace/@participations HTTP/1.1
    """
    def reply(self):
        token = self.read_params()
        if token:
            return self.prepare_response_item(self.find_participant(
                token, self.context.get_context_with_local_roles()))
        else:
            result = {}
            result['items'] = self.get_response_items()
            return result

    def get_response_items(self):
        return [self.prepare_response_item(item) for item in
                self.participants(self.context.get_context_with_local_roles())]

    def read_params(self):
        if len(self.params) == 1:
            return self.params[0]
        return None


class ParticipationsDelete(ParticipationTraverseService):

    def reply(self):
        token = self.read_params()

        self.recursive_delete_participation(self.context, token)
        self.request.response.setStatus(204)
        return None

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply token ID as URL path parameters.")

        return self.params[0]

    def recursive_delete_participation(self, obj, token):
        """It is possible that a subfolder has blocked the role inheritance
        and has assigned it's own roles for a specific user. We have to be sure
        that this user will be deleted in the whole tree and not only in the
        current context.
        """
        if obj.get_context_with_local_roles() == obj and self.find_participant(token, obj):
                manager = ManageParticipants(obj, self.request)
                manager._delete('user', token)

        for folder in obj.listFolderContents(
                contentFilter={'portal_type': 'opengever.workspace.folder'}):
            self.recursive_delete_participation(folder, token)


class ParticipationsPatch(ParticipationTraverseService):

    def reply(self):
        token = self.read_params()
        data = self.validate_data(json_body(self.request))

        manager = ManageParticipants(self.context, self.request)
        manager._modify(token, data.get('role').get('token'), 'user')
        return None

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply token ID as URL path parameters.")

        return self.params[0]

    def validate_data(self, data):
        if not data.get('role'):
            raise BadRequest('Missing parameter role')

        return data


class ParticipationsPost(ParticipationTraverseService):

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        token, role = self.validate_data(json_body(self.request))

        self.validate_participation(token, role)

        assignment = SharingRoleAssignment(token, [role], self.context)
        RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

        activity_manager = WorkspaceWatcherManager(self.context)
        activity_manager.new_participant_added(token, role)

        self.request.response.setStatus(201)
        return self.prepare_response_item(self.find_participant(
            token, self.context.get_context_with_local_roles()))

    def validate_data(self, data):
        token = data.get('token')
        role = data.get('role')

        if not token:
            raise BadRequest('Missing parameter token')

        if not role:
            raise BadRequest('Missing parameter role')

        return token, role

    def validate_participation(self, token, role):
        if not self.context.has_blocked_local_role_inheritance():
            raise Forbidden(
                "The participations are not managed in this context. "
                "Please block the role inheritance before adding "
                "new participants.")

        if not self.find_participant(token, self.context.get_parent_with_local_roles()):
            raise BadRequest('The participant is not allowed')

        if self.find_participant(token, self.context.get_context_with_local_roles()):
            raise BadRequest('The participant already exists')

        if role not in PARTICIPATION_ROLES:
            raise BadRequest('Role is not availalbe. Available roles are: {}'.format(
                PARTICIPATION_ROLES.keys()))
