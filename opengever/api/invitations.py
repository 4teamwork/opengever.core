from opengever.api import _
from opengever.api.participations import ParticipationTraverseService
from opengever.api.validation import get_validation_errors
from opengever.workspace import is_invitation_feature_enabled
from opengever.workspace.invitation import IWorkspaceInvitationSchema
from opengever.workspace.participation import invitation_to_item
from opengever.workspace.participation import TYPE_INVITATION
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.participation.browser.my_invitations import MyWorkspaceInvitations
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides


class InvitationsGet(Service):
    """API Endpoint which returns a list of all invitations for the current
    workspace.

    GET workspace/@invitations HTTP/1.1
    """

    def reply(self):
        result = {}
        result['items'] = self.get_response_items()
        return result

    def get_response_items(self):
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
                'comment': invitation.get('comment'),
                'created': json_compatible(invitation.get('created')),
            })

        result['items'] = items
        return result


class WorkspaceInvitationsPost(ParticipationTraverseService):
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
                "the id: {}".format(iid))

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


class InvitationsDelete(ParticipationTraverseService):

    def reply(self):
        token = self.read_params()

        manager = ManageParticipants(self.context, self.request)
        manager._delete('invitation', token)
        self.request.response.setStatus(204)
        return None

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest(
                "Must supply token ID as URL path parameters.")

        return self.params[0]


class InvitationsPost(ParticipationTraverseService):

    def reply(self):

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if not is_invitation_feature_enabled():
            raise Forbidden(_("Invitations are disabled."))

        data = json_body(self.request)
        data['role'] = data.get('role', {}).get('token')
        errors = get_validation_errors(data, IWorkspaceInvitationSchema,
                                       allow_unknown_fields=True)
        if errors:
            raise BadRequest(errors)

        inviter_id = api.user.get_current().getId()
        storage = getUtility(IInvitationStorage)
        iid = storage.add_invitation(self.context,
                                     data['recipient_email'],
                                     inviter_id,
                                     data['role'],
                                     comment=data.get('comment', u''))

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', self.context.absolute_url())
        invitation = storage.get_invitation(iid)
        return invitation_to_item(invitation, self.context)
