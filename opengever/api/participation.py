from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation import PARTICIPATION_TYPES
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone.restapi.services import Service


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


class ParticipationsGet(Service):
    """API Endpoint which returns a list of all participants for the current
    workspace.

    GET workspace/@participations HTTP/1.1
    """

    def reply(self):
        result = {}
        self.extend_with_roles(result)
        self.extend_with_participations(result)
        return result

    def extend_with_roles(self, result):
        result['roles'] = map(lambda role: role.serialize(self.request),
                              PARTICIPATION_ROLES.values())

    def extend_with_participations(self, result):
        manager = ManageParticipants(self.context, self.request)
        participants = manager.get_participants() + manager.get_pending_invitations()
        result['items'] = []
        for participant in participants:
            result['items'].append(participation_item(
                self.context, self.request,
                token=participant.get('token'),
                participation_type=PARTICIPATION_TYPES[participant.get('type_')],
                editable=participant.get('can_manage'),
                role=participant.get('roles')[0],
                participant_fullname=participant.get('name'),
                inviter_fullname=participant.get('inviter')
                ))
