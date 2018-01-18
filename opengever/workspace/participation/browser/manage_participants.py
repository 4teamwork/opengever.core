from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.protect import CheckAuthenticator
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
import json


class ManageParticipants(BrowserView):

    def __call__(self):
        return self.json_response(
            self.get_participants() + self.get_pending_invitations()
        )

    def json_response(self, data):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        return json.dumps(data)

    def get_participants(self):
        return self.get_user_role_mapping()

    def get_user_role_mapping(self):
        """Get local roles mapping for all local users.
        """
        entries = []

        for userid, roles in self.context.get_local_roles():
            member = api.user.get(userid=userid)
            if member is not None:
                item = dict(userid=userid,
                            roles=roles,
                            can_manage=self.can_manage_member(member),
                            type_='user',
                            name=self.get_full_user_info(member=member))
                entries.append(item)
        return entries

    def can_manage_member(self, member=None):

        if member and member.getId() == api.user.get_current().getId():
            return False
        else:
            return api.user.has_permission(
                'Sharing page: Delegate WorkspaceAdmin role',
                obj=self.context)

    def get_pending_invitations(self):
        storage = IInvitationStorage(self.context)
        entries = []

        for invitation in storage.get_invitations_for_context(self.context):
            item = dict(name=self.get_full_user_info(userid=invitation.userid),
                        roles=invitation.role,
                        inviter=self.get_full_user_info(userid=invitation.inviter),
                        can_manage=self.can_manage_member(),
                        type_='invitation',
                        iid=invitation.iid)
            entries.append(item)

        return entries

    def get_full_user_info(self, userid=None, member=None):
        if member is None:
            member = api.user.get(userid=userid)

        email = member.getProperty('email', '').decode('utf-8')
        name = member.getProperty('fullname', '').decode('utf-8')

        if name and email:
            return u'{} ({})'.format(name, email)
        elif name:
            return name
        else:
            return userid.decode('utf-8')

    def add(self):
        """A traversable method to add new invitations"""
        CheckAuthenticator(self.request)
        userid = self.request.get('userid', None)
        role = self.request.get('role', None)

        if not userid or not role or not self.can_manage_member():
            raise BadRequest('No userid provided')

        invitation = Invitation(self.context, userid,
                                api.user.get_current().getId(), role)

        storage = IInvitationStorage(self.context)
        storage.add_invitation(invitation)
        return self.__call__()

    def delete(self):
        """ A traversable method to delete a pending invitation"""
        CheckAuthenticator(self.request)

        token = self.request.get('token', None)
        type_ = self.request.get('type', None)

        if not token or not type_:
            raise BadRequest('A token a a type is required')

        if type_ == 'invitation':
            storage = IInvitationStorage(self.context)
            invitation = storage.get_invitation_by_iid(token)
            if storage.remove_invitation(invitation):
                return self.__call__()
            else:
                raise BadRequest('Was not able to delete the invitation')
