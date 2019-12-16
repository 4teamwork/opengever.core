from itsdangerous import URLSafeTimedSerializer
from opengever.base.casauth import get_gever_portal_url
from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import PloneUserActor
from opengever.ogds.base.utils import ogds_service
from opengever.workspace import _
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.config import workspace_config
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from urllib import urlencode
from zExceptions import BadRequest
from zExceptions import InternalError
from zope.component import getUtility


class MyWorkspaceInvitations(BrowserView):

    template = ViewPageTemplateFile('templates/my-invitations.pt')

    def __call__(self):

        return self.template()

    def is_feature_enabled(self):
        return is_workspace_feature_enabled()

    def storage(self):
        return getUtility(IInvitationStorage)

    def get_invitations(self):
        email = api.user.get_current().getProperty('email')
        target_title = _(u'Deleted Workspace')

        entries = list(self.storage().iter_invitations_for_recipient_email(email))
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
        iid = self.request.get('iid', None)

        if iid is None:
            raise BadRequest('No iid given')

        invitation = self._get_invitation(iid)
        if not invitation:
            raise BadRequest('Wrong invitation')

        return self._get_invitation(iid)

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

    def _serialize_and_sign_payload(self, payload):
        """Serialize and sign the payload for the portal
        """
        secret = workspace_config.secret
        serializer = URLSafeTimedSerializer(secret)
        return serializer.dumps(payload)

    def accept(self):
        """Accept an invitation. There are 3 different scenarios here:
        1. The user is not logged in and his E-mail address does not match any
           user. In that case we redirect to the portal registration.
        2. The user is not logged in but his E-mail address matches that of an
           existing user. In that case we redirect to the portal login.
        3. The user is logged-in. In that case we accept the invitation by
           setting the role and redirect the user to the workspace.
        """
        invitation = self.get_invitation_and_validate_payload()
        with elevated_privileges():
            target_workspace = uuidToObject(invitation['target_uuid'])

        if api.user.is_anonymous():
            accept_url = "{}/@@my-invitations/accept".format(
                target_workspace.absolute_url())
            accept_params = {'iid': invitation['iid']}

            if not self.storage()._find_user_id_for_email(invitation['recipient_email']):
                accept_params['new_user'] = 1
                accept_url = "{}?{}".format(
                    accept_url, urlencode(accept_params))
                group_dn = self._get_orgunit_group_dn()

                params = {'email': invitation['recipient_email'],
                          'callback': accept_url,
                          'group': group_dn
                          }
                payload = self._serialize_and_sign_payload(params)
                redirect_url = "{}/registration?invitation={}".format(
                    get_gever_portal_url(), payload)

            else:
                accept_url = "{}?{}".format(
                    accept_url, urlencode(accept_params))
                params = {'redirect_url': accept_url}
                redirect_url = "{}/login?{}".format(
                    get_gever_portal_url(), urlencode(params))

            return self.request.RESPONSE.redirect(redirect_url)
        target = self._accept(invitation)
        return self.request.RESPONSE.redirect(target.absolute_url())

    def _accept(self, invitation):
        with elevated_privileges():
            target = uuidToObject(invitation['target_uuid'])

            assignment = InvitationRoleAssignment(
                invitation['recipient'], [invitation['role']], target)
            RoleAssignmentManager(target).add_or_update_assignment(assignment)
            self.storage().remove_invitation(invitation['iid'])

            manager = WorkspaceWatcherManager(self.context)
            manager.new_participant_added(invitation['recipient'], invitation['role'])

        return target

    def decline(self):
        """Decline invitation by deleting the invitation from the storage.
        """
        invitation = self.get_invitation_and_validate_payload()
        self._decline(invitation)
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/' + self.__name__)

    def _decline(self, invitation):
        self.storage().remove_invitation(invitation.get('iid'))
