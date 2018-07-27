from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.ogds.base.actor import PloneUserActor
from opengever.ogds.base.sources import AllUsersSource
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.app.workflow.interfaces import ISharingPageRole
from plone.batching.batch import Batch
from plone.protect import CheckAuthenticator
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getUtility
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
        return json.dumps(data)

    def get_participants(self):
        """Get list of users with all managed local roles.
        """
        entries = []

        for userid, roles in self.context.get_local_roles():
            member = api.user.get(userid=userid)
            if member is not None:
                item = dict(token=userid,
                            roles=list(set(roles) & set(
                                MANAGED_ROLES + ['WorkspaceOwner'])),
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
        storage = getUtility(IInvitationStorage)
        entries = []

        for invitation in storage.iter_invitions_for_context(self.context):
            item = dict(name=self.get_full_user_info(userid=invitation['recipient']),
                        roles=[invitation['role']],
                        inviter=self.get_full_user_info(
                            userid=invitation['inviter']),
                        can_manage=self.can_manage_member(),
                        type_='invitation',
                        token=invitation['iid'])
            entries.append(item)

        return entries

    def get_full_user_info(self, userid=None, member=None):
        if member is None:
            member = api.user.get(userid=userid)

        if userid is None:
            userid = member.getId()

        return PloneUserActor(identifier=userid, user=member).get_label()

    def user_has_permission(self, role):
        permission = getUtility(ISharingPageRole, name=role).required_permission
        return api.user.has_permission(permission, obj=self.context)

    def add(self):
        """A traversable method to add new invitations"""
        CheckAuthenticator(self.request)
        userid = self.request.get('userid', None)
        role = self.request.get('role', None)

        if not userid or not role or not self.can_manage_member():
            raise BadRequest('No userid or role provided')

        if role not in MANAGED_ROLES and not self.user_has_permission(role):
            raise Unauthorized('No allowed to delegate this permission')

        storage = getUtility(IInvitationStorage)
        storage.add_invitation(self.context, userid,
                               api.user.get_current().getId(), role)
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
            storage = getUtility(IInvitationStorage)
            storage.remove_invitation(token)
            return self.__call__()

        elif type_ == 'user' and self.can_manage_member(api.user.get(userid=token)):
            RoleAssignmentManager(self.context).clear_by_cause_and_principal(
                ASSIGNMENT_VIA_INVITATION, token)
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
                assignment = InvitationRoleAssignment(token, [role], self.context)
                RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

                self.context.setModificationDate()
                self.context.reindexObject(idxs=['modified'])
                self.request.RESPONSE.setStatus(204)
                return ''
            else:
                raise BadRequest('User does not have any local roles')
        elif type_ == 'invitation':
            storage = getUtility(IInvitationStorage)
            storage.update_invitation(token, role=role)
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
