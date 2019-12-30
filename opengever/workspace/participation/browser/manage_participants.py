from opengever.base.role_assignments import ASSIGNMENT_VIA_INVITATION
from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.ogds.base.sources import PotentialWorkspaceMembersSource
from opengever.workspace.participation import can_manage_member
from opengever.workspace.participation import get_full_user_info
from opengever.workspace.participation import invitation_to_item
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
                            roles=list(set(roles) & set(MANAGED_ROLES)),
                            can_manage=can_manage_member(self.context, member, roles),
                            type_='user',
                            name=get_full_user_info(member=member),
                            userid=userid)
                entries.append(item)
        return entries

    def get_pending_invitations(self):
        storage = getUtility(IInvitationStorage)
        entries = []

        for invitation in storage.iter_invitations_for_context(self.context):
            entries.append(invitation_to_item(invitation, self.context))

        return entries

    def user_has_permission(self, role):
        permission = getUtility(ISharingPageRole, name=role).required_permission
        return api.user.has_permission(permission, obj=self.context)

    def add(self):
        """A traversable method to add new invitations"""
        CheckAuthenticator(self.request)
        userid = self.request.get('userid', None)
        role = self.request.get('role', None)
        self._add(userid, role)
        return self.__call__()

    def _add(self, userid, role):
        if not userid or not role or not can_manage_member(self.context):
            raise BadRequest('No userid or role provided')

        if role not in MANAGED_ROLES and not self.user_has_permission(role):
            raise Unauthorized('No allowed to delegate this permission')

        if userid not in self.get_user_source():
            raise BadRequest('User cannot be added to workspace')

        storage = getUtility(IInvitationStorage)
        iid = storage.add_invitation(self.context, userid,
                                     api.user.get_current().getId(), role)
        return storage.get_invitation(iid)

    def delete(self):
        """A traversable method to delete a pending invitation or local roles.
        """

        CheckAuthenticator(self.request)

        token = self.request.get('token', None)
        type_ = self.request.get('type', None)

        if not token or not type_:
            raise BadRequest('A token and a type is required')

        self._delete(type_, token)
        return self.__call__()

    def _delete(self, type_, token):
        if type_ == 'invitation' and can_manage_member(self.context):
            storage = getUtility(IInvitationStorage)
            storage.remove_invitation(token)
            return

        elif type_ == 'user' and can_manage_member(self.context, api.user.get(userid=token)):
            RoleAssignmentManager(self.context).clear_by_cause_and_principal(
                ASSIGNMENT_VIA_INVITATION, token)
            # Avoid circular imports
            from opengever.workspace.activities import WorkspaceWatcherManager
            manager = WorkspaceWatcherManager(self.context)
            manager.participant_removed(token)
            return
        else:
            raise BadRequest('Oh my, something went wrong')

    def modify(self):
        """ A traversable method to modify a users local roles"""
        CheckAuthenticator(self.request)

        token = self.request.get('token', None)
        role = self.request.get('role', None)
        type_ = self.request.get('type', None)
        self._modify(token, role, type_)
        return ''

    def _modify(self, token, role, type_):
        if not token or not type_:
            raise BadRequest('No userid or type provided.')

        if role not in MANAGED_ROLES:
            raise Unauthorized('Inavlid role provided.')

        if token == api.user.get_current().id:
            raise Unauthorized('Not allowed to modify the current user.')

        if type_ == 'user':
            user_roles = api.user.get_roles(username=token, obj=self.context,
                                            inherit=False)
            if user_roles:
                assignment = InvitationRoleAssignment(token, [role], self.context)
                RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

                self.context.setModificationDate()
                self.context.reindexObject(idxs=['modified'])
                self.request.RESPONSE.setStatus(204)
                return True
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

        source = self.get_user_source()
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

    def get_user_source(self):
        return PotentialWorkspaceMembersSource(self.context)
