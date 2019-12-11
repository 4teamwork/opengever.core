from opengever.api.participations import ParticipationsGet
from opengever.api.participations import ParticipationTraverseService
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


class InvitationsGet(ParticipationsGet):
    """API Endpoint which returns a list of all invitations for the current
    workspace.

    GET workspace/@invitations HTTP/1.1
    """

    def _items(self):
        manager = ManageParticipants(self.context, self.request)
        return manager.get_pending_invitations()


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


class InvitationsPatch(ParticipationTraverseService):

    def reply(self):
        token = self.read_params()
        data = self.validate_data(json_body(self.request))

        manager = ManageParticipants(self.context, self.request)
        manager._modify(token, data.get('role').get('token'), 'invitation')
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
