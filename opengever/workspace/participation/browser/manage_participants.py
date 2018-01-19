from opengever.ogds.base.sources import AllUsersSource
from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.batching.batch import Batch
from plone.protect import CheckAuthenticator
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zExceptions import Unauthorized
import json


MANAGED_ROLES = ['WorkspaceGuest', 'WorkspaceMember', 'WorkspaceAdmin']


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
                item = dict(token=userid,
                            roles=list(set(roles) & set(MANAGED_ROLES + ['WorkspaceOwner'])),
                            can_manage=self.can_manage_member(member, roles),
                            type_='user',
                            name=self.get_full_user_info(member=member))
                entries.append(item)
        return entries

    def can_manage_member(self, member=None, roles=None):

        if member and member.getId() == api.user.get_current().getId():
            return False
        elif roles and 'WorkspaceOwner' in roles:
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
                        roles=[invitation.role],
                        inviter=self.get_full_user_info(
                            userid=invitation.inviter),
                        can_manage=self.can_manage_member(),
                        type_='invitation',
                        token=invitation.iid)
            entries.append(item)

        return entries

    def get_full_user_info(self, userid=None, member=None):
        if member is None:
            member = api.user.get(userid=userid)

        email = member.getProperty('email', '')
        name = member.getProperty('fullname', '')

        if name and email:
            return u'{} ({})'.format(name.decode('utf-8'),
                                     email.decode('utf-8'))
        elif name:
            return name.decode('utf-8')
        elif member:
            return member.getId().decode('utf-8')
        else:
            return userid.decode('utf-8')

    def add(self):
        """A traversable method to add new invitations"""
        CheckAuthenticator(self.request)
        userid = self.request.get('userid', None)
        role = self.request.get('role', None)

        if not userid or not role or not self.can_manage_member():
            raise BadRequest('No userid or role provided')

        invitation = Invitation(self.context, userid,
                                api.user.get_current().getId(), role)

        storage = IInvitationStorage(self.context)
        storage.add_invitation(invitation)
        return self.__call__()

    def delete(self):
        """A traversable method to delete a pending invitation or local roles.
        """

        CheckAuthenticator(self.request)

        token = self.request.get('token', None)
        type_ = self.request.get('type', None)

        if not token or not type_:
            raise BadRequest('A token and a type is required')

        if type_ == 'invitation' and self.can_manage_member():
            storage = IInvitationStorage(self.context)
            invitation = storage.get_invitation_by_iid(token)
            if storage.remove_invitation(invitation):
                return self.__call__()
            else:
                raise BadRequest('Was not able to delete the invitation')

        elif type_ == 'user' and self.can_manage_member(api.user.get(userid=token)):
            self.context.manage_delLocalRoles([token])
            self.context.reindexObjectSecurity()
            return self.__call__()
        else:
            raise BadRequest('Oh my, something went wrong')

    def modify(self):
        """ A traversable method to modify a users local roles"""
        CheckAuthenticator(self.request)

        token = self.request.get('token', None)
        role = self.request.get('role', None)
        type_ = self.request.get('type', None)

        if not token or not type_:
            raise BadRequest('No userid or type provided.')

        if role not in MANAGED_ROLES:
            raise Unauthorized('Inavlid role provided.')

        if type_ == 'user':
            user_roles = api.user.get_roles(username=token, obj=self.context,
                                            inherit=False)
            if user_roles and 'WorkspaceOwner' not in user_roles:
                self.context.manage_setLocalRoles(token, [role])
                self.request.RESPONSE.setStatus(204)
                return ''
            else:
                raise BadRequest('User does not have any local roles')
        elif type_ == 'invitation':
            storage = IInvitationStorage(self.context)
            invitation = storage.get_invitation_by_iid(token)
            invitation.role = role
        else:
            raise BadRequest('Wrong type')

    def search(self):
        """ A traversable method to search for users"""
        query = self.request.get('q', None)
        page = int(self.request.get('page', 1))
        pagesize = int(self.request.get('pagesize', 20))

        if not query:
            return json.dumps({})

        source = AllUsersSource(api.portal.get())
        batch = Batch.fromPagenumber(items=source.search(query),
                                     pagesize=pagesize,
                                     pagenumber=page)

        def _term_to_dict(term):
            return {'_resultId': term.token,
                    'id': term.token,
                    'text': term.title and term.title or term.token}

        return json.dumps(
            {
                'results': map(_term_to_dict, batch),
                'total_count': len(batch),
                'page': page,
                'pagination': {'more': (page * pagesize) < len(batch)}
            }
        )
