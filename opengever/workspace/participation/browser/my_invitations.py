from opengever.base.casauth import get_gever_portal_url
from opengever.base.model import create_session
from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import PloneUserActor
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.workspace import _
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.participation import load_signed_payload
from opengever.workspace.participation import serialize_and_sign_payload
from opengever.workspace.participation.storage import IInvitationStorage
from opengever.workspace.participation.storage import STATE_PENDING
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from urllib import urlencode
from zExceptions import BadRequest
from zExceptions import InternalError
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.interface import alsoProvides


class MyWorkspaceInvitations(BrowserView):

    def __call__(self):
        raise NotFound()

    def is_feature_enabled(self):
        return is_workspace_feature_enabled()

    def storage(self):
        return getUtility(IInvitationStorage)

    def get_invitations(self):
        target_title = _(u'Deleted Workspace')

        entries = list(self.storage().iter_invitations_for_current_user())
        entries.sort(key=lambda item: item['created'])

        for entry in entries:
            with elevated_privileges():
                target = uuidToObject(entry['target_uuid'])
                if target:
                    target_title = target.Title()

            if target:
                inviter = PloneUserActor(entry['inviter'],
                                         user=api.user.get(entry['inviter']))
                yield {'inviter': inviter.get_label(),
                       'target_title': target_title,
                       'iid': entry['iid'],
                       'created': entry['created'],
                       'comment': entry['comment']
                       }

    def get_invitation_and_validate_payload(self):
        payload = load_signed_payload(self.request.get('invitation'))
        iid = payload.pop('iid', None)

        if iid is None:
            raise BadRequest('No iid given')

        invitation = self._get_invitation(iid)
        if not invitation:
            raise BadRequest('Wrong invitation')
        if invitation['status'] != STATE_PENDING:
            raise BadRequest('Invitation not pending')

        return self._get_invitation(iid), payload

    def _get_invitation(self, iid):
        try:
            invitation = self.storage().get_invitation(iid)
        except KeyError:
            return None

        return invitation

    def _get_orgunit_group_dn(self):
        """get the dn of the group associated with the current orgunit
        """
        portal = api.portal.get()
        org_units = ogds_service().all_org_units()
        if len(org_units) > 1:
            raise InternalError("Workspace installation can only have a "
                                "single enabled org_unit")
        group_id = org_units[0].users_group_id
        groups = []
        for item in portal['acl_users'].objectValues():
            if ILDAPMultiPlugin.providedBy(item):
                user_folder = item.acl_users
                key = user_folder.groupid_attr
                groups.extend(user_folder.searchGroups(
                    **{key: group_id, 'exactMatch': True})
                )
        if len(groups) > 1:
            raise InternalError("group {} is not unique".format(group_id))
        return groups[0]['dn']

    def accept(self):
        """Accept an invitation. There are 3 different scenarios here:
        1. The user is not logged in and his E-mail address does not match any
           user. In that case we redirect to the portal registration.
        2. The user is not logged in but his E-mail address matches that of an
           existing user. In that case we redirect to the portal login.
        3. The user is logged-in. In that case we accept the invitation by
           setting the role and redirect the user to the workspace.
        """
        alsoProvides(self.request, IDisableCSRFProtection)

        invitation, payload = self.get_invitation_and_validate_payload()
        with elevated_privileges():
            target_workspace = uuidToObject(invitation['target_uuid'])

        if api.user.is_anonymous():
            if payload.get("no_redirect", None):
                # User just registered or logged in on the portal
                # but does not have a GEVER session yet.
                raise Unauthorized

            accept_url = "{}/@@my-invitations/accept".format(
                target_workspace.absolute_url())
            accept_params = {'iid': invitation['iid'],
                             'no_redirect': 1}

            if not self.storage()._find_user_id_for_email(invitation['recipient_email']):
                accept_params['new_user'] = 1
                accept_url = "{}?invitation={}".format(
                    accept_url, serialize_and_sign_payload(accept_params))
                group_dn = self._get_orgunit_group_dn()

                params = {'email': invitation['recipient_email'],
                          'callback': accept_url,
                          'group': group_dn
                          }
                payload = serialize_and_sign_payload(params)
                redirect_url = "{}/registration?invitation={}".format(
                    get_gever_portal_url(), payload)

            else:
                accept_url = "{}?invitation={}".format(
                    accept_url, serialize_and_sign_payload(accept_params))
                params = {'redirect_url': accept_url}
                redirect_url = "{}/login?{}".format(
                    get_gever_portal_url(), urlencode(params))

            return self.request.RESPONSE.redirect(redirect_url)

        target = self._accept(invitation)
        self._create_ogds_entry()
        return self.request.RESPONSE.redirect(target.absolute_url())

    def _create_ogds_entry(self):
        session = create_session()
        member = api.user.get_current()
        userid = member.getId()
        firstname = member.getProperty('firstname', '')
        lastname = member.getProperty('lastname', '')
        email = member.getProperty('email')
        ogds_user = User(
            userid=userid,
            firstname=firstname,
            lastname=lastname,
            email=email)

        # Assign the intersection of existing OGDS groups and the newly created
        # user's groups as groups for the new OGDS user entry. This will most
        # likely be just the OrgUnit's users_group. If there's more, they
        # will be created and assigned during next sync.
        groups_of_new_user = member.getUser().getGroupIds()
        groups = Group.query.filter(Group.groupid.in_(groups_of_new_user)).all()
        ogds_user.groups = groups
        session.add(ogds_user)

    def _accept(self, invitation):
        with elevated_privileges():
            target = uuidToObject(invitation['target_uuid'])
            self.storage().map_email_to_current_userid_for_all_invitations(
                invitation['recipient_email'])
            # recipient was set in the invitation, so we need to fetch it anew
            invitation = self.storage().get_invitation(invitation['iid'])

            assignment = InvitationRoleAssignment(
                invitation['recipient'], [invitation['role']], target)
            RoleAssignmentManager(target).add_or_update_assignment(assignment)
            self.storage().mark_invitation_as_accepted(invitation['iid'])

            manager = WorkspaceWatcherManager(self.context)
            manager.new_participant_added(invitation['recipient'], invitation['role'])

        return target

    def decline(self):
        """Decline invitation by deleting the invitation from the storage.
        """
        alsoProvides(self.request, IDisableCSRFProtection)

        invitation, payload = self.get_invitation_and_validate_payload()
        self._decline(invitation)
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/' + self.__name__)

    def _decline(self, invitation):
        self.storage().mark_invitation_as_declined(invitation['iid'])
