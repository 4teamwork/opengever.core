from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation import PARTICIPATION_TYPES
from opengever.workspace.participation import PARTICIPATION_TYPES_BY_PATH_IDENTIFIER
from opengever.workspace.participation import TYPE_INVITATION
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


def participation_item(
        context, request, token,
        participation_type, editable, role, participant_fullname, inviter_fullname):

    return {
        '@id': '{}/@participations/{}/{}'.format(
            context.absolute_url(),
            participation_type.path_identifier,
            token),
        '@type': 'virtual.participations.{}'.format(participation_type.id),
        'participant_fullname': participant_fullname,
        'inviter_fullname': inviter_fullname,
        'role': role,
        'readable_role': PARTICIPATION_ROLES.get(role).translated_title(request),
        'is_editable': editable,
        'participation_type': participation_type.id,
        'readable_participation_type': participation_type.translated_title(request),
        'token': token,
    }


class ParticipationTraverseService(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ParticipationTraverseService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@participations as parameters
        self.params.append(name)
        return self


class ParticipationsGet(ParticipationTraverseService):
    """API Endpoint which returns a list of all participants for the current
    workspace.

    GET workspace/@participations HTTP/1.1
    """

    def reply(self):
        token = self.read_params()
        if token:
            return self._participant(token)
        else:
            result = {}
            self.extend_with_roles(result)
            self.extend_with_participations(result)
            return result

    def extend_with_roles(self, result):
        result['roles'] = map(lambda role: role.serialize(self.request),
                              PARTICIPATION_ROLES.values())

    def extend_with_participations(self, result):
        result['items'] = list(self._participations())

    def _participations(self):
        manager = ManageParticipants(self.context, self.request)
        participants = manager.get_participants() + manager.get_pending_invitations()
        for participant in participants:
            yield participation_item(
                self.context, self.request,
                token=participant.get('token'),
                participation_type=PARTICIPATION_TYPES[participant.get('type_')],
                editable=participant.get('can_manage'),
                role=participant.get('roles')[0],
                participant_fullname=participant.get('name'),
                inviter_fullname=participant.get('inviter')
                )

    def _participant(self, token):
        for participant in self._participations():
            if participant.get('token') == token:
                return participant

    def read_params(self):
        if len(self.params) == 2:
            return self.params[1]
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

        manager = ManageParticipants(self.context, self.request)
        invitation = manager._add(data.get('userid'), data.get('role'))
        return participation_item(
            self.context, self.request,
            token=invitation['iid'],
            participation_type=PARTICIPATION_TYPES['invitation'],
            editable=manager.can_manage_member(),
            role=invitation['role'],
            participant_fullname=manager.get_full_user_info(userid=invitation['recipient']),
            inviter_fullname=manager.get_full_user_info(userid=invitation['inviter'])
            )

    def validate_params(self):
        if len(self.params) != 1 or self.params[0] != TYPE_INVITATION.path_identifier:
            raise NotFound

    def validate_data(self, data):
        if not data.get('userid'):
            raise BadRequest('Missing parameter userid')

        if not data.get('role'):
            raise BadRequest('Missing parameter role')

        return data


class ParticipationsPatch(ParticipationTraverseService):

    def reply(self):
        participation_type, token = self.read_params()
        data = self.validate_data(json_body(self.request))

        manager = ManageParticipants(self.context, self.request)
        manager._modify(token, data.get('role'), participation_type.id)
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
