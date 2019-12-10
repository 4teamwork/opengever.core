from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation import PARTICIPATION_TYPES
from opengever.workspace.participation import PARTICIPATION_TYPES_BY_PATH_IDENTIFIER
from opengever.workspace.participation import TYPE_INVITATION
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.participation.browser.my_invitations import MyWorkspaceInvitations
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import getMultiAdapter
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
        token = participant.get('token')
        participation_type = PARTICIPATION_TYPES[participant.get('type_')]
        role = participant.get('roles')[0]
        return {
            '@id': '{}/@{}/{}'.format(
                self.context.absolute_url(),
                participation_type.path_identifier,
                token),
            '@type': 'virtual.participations.{}'.format(participation_type.id),
            'participant_fullname': participant.get('name'),
            'inviter_fullname': participant.get('inviter'),
            'role': role,
            'readable_role': PARTICIPATION_ROLES.get(role).translated_title(self.request),
            'is_editable': participant.get('can_manage'),
            'participation_type': participation_type.id,
            'readable_participation_type': participation_type.translated_title(self.request),
            'token': token,
        }


class ParticipationsGet(ParticipationTraverseService):
    """API Endpoint which returns a list of all participants for the current
    workspace.

    GET workspace/@participations HTTP/1.1
    """

    def reply(self):
        token = self.read_params()
        if token:
            return self.get_response_item(token)
        else:
            result = {}
            result['items'] = self.get_response_items()
            return result

    def get_response_items(self):
        return [self.prepare_response_item(item) for item in self._items()]

    def _items(self):
        manager = ManageParticipants(self.context, self.request)
        return manager.get_participants()

    def get_response_item(self, token):
        for item in self._items():
            if item.get('token') == token:
                return self.prepare_response_item(item)

    def read_params(self):
        if len(self.params) == 1:
            return self.params[0]
        return None


class ParticipationsDelete(ParticipationTraverseService):

    def reply(self):
        path_identifier, token = self.read_params()
        participation_type = PARTICIPATION_TYPES_BY_PATH_IDENTIFIER.get(
            path_identifier)

        manager = ManageParticipants(self.context, self.request)
        manager._delete(participation_type.id, token)
        self.request.response.setStatus(204)
        return None

    def read_params(self):
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply type and token ID as URL path parameters.")

        return self.params[0], self.params[1]


class ParticipationsPost(ParticipationTraverseService):

    def reply(self):
        self.validate_params()
        data = self.validate_data(json_body(self.request))
        userid = data.get('user').get('token')
        role = data.get('role').get('token')
        if not self.validate_duplicated_users(userid):
            raise BadRequest("User already participate to this workspace")

        manager = ManageParticipants(self.context, self.request)
        invitation = manager.invitation_to_item(manager._add(userid, role))
        return self.prepare_response_item(invitation)

    def validate_duplicated_users(self, userid):
        manager = ManageParticipants(self.context, self.request)
        participants = manager.get_participants() + manager.get_pending_invitations()
        existing_users = filter(lambda p: p.get('userid') == userid, participants)
        return len(existing_users) == 0

    def validate_params(self):
        if len(self.params) != 1 or self.params[0] != TYPE_INVITATION.path_identifier:
            raise NotFound

    def validate_data(self, data):
        if not data.get('user'):
            raise BadRequest('Missing parameter userid')

        if not data.get('role'):
            raise BadRequest('Missing parameter role')

        return data


class ParticipationsPatch(ParticipationTraverseService):

    def reply(self):
        participation_type, token = self.read_params()
        data = self.validate_data(json_body(self.request))

        manager = ManageParticipants(self.context, self.request)
        manager._modify(token, data.get('role').get('token'), participation_type.id)
        return None

    def read_params(self):
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply type and token ID as URL path parameters.")

        return PARTICIPATION_TYPES_BY_PATH_IDENTIFIER.get(self.params[0]), self.params[1]

    def validate_data(self, data):
        if not data.get('role'):
            raise BadRequest('Missing parameter role')

        return data


class MyInvitationsGet(Service):
    """API Endpoint which returns a list of all invitations for the current user

    GET /@my-workspace-invitations HTTP/1.1
    """

    def reply(self):
        result = {}
        items = []
        invitations = MyWorkspaceInvitations(self.context, self.request).get_invitations()

        for invitation in invitations:
            base_url = '{}/@workspace-invitations/{}'.format(
                self.context.absolute_url(),
                invitation.get('iid'))
            items.append({
                '@id': base_url,
                '@type': 'virtual.participations.{}'.format(TYPE_INVITATION.id),
                'accept': '{}/accept'.format(base_url),
                'decline': '{}/decline'.format(base_url),
                'title': invitation.get('target_title'),
                'inviter_fullname': invitation.get('inviter'),
                'created': json_compatible(invitation.get('created')),
                })

        result['items'] = items
        return result


class InvitationsPost(ParticipationTraverseService):
    """API Endpoint for accepting or declining invitations.

    POST /@workspace-invitations/{invitation_id}/{action} HTTP/1.1
    """
    available_actions = ['decline', 'accept']

    def reply(self):
        iid, action = self.read_params()

        if action not in self.available_actions:
            raise NotFound

        my_invitations_manager = MyWorkspaceInvitations(self.context, self.request)
        invitation = my_invitations_manager._get_invitation(iid)

        if not invitation:
            raise BadRequest(
                "There is no invitation for the current user with "
                "the id: ".format(iid))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if action == 'decline':
            my_invitations_manager._decline(invitation)
            return self.request.response.setStatus(204)

        if action == 'accept':
            target = my_invitations_manager._accept(invitation)
            return getMultiAdapter(
                (target, self.request), ISerializeToJson)(include_items=False)

    def read_params(self):
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply an invitation ID and an action (accept/decline)")

        return self.params[0], self.params[1]
