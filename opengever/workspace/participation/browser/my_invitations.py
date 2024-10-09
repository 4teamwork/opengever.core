from logging import getLogger
from opengever.base.casauth import get_gever_portal_url
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.workspace import _
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.interfaces import IWorkspaceSettings
from opengever.workspace.participation import load_signed_payload
from opengever.workspace.participation import serialize_and_sign_payload
from opengever.workspace.participation.storage import IInvitationStorage
from opengever.workspace.participation.storage import STATE_PENDING
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from urllib import urlencode
from zExceptions import BadRequest
from zExceptions import InternalError
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.interface import alsoProvides


logger = getLogger('opengever.workspace.participation')


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
                inviter = Actor.lookup(entry['inviter'])
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

        return invitation, payload

    def _get_invitation(self, iid):
        try:
            invitation = self.storage().get_invitation(iid)
        except KeyError:
            return None

        return invitation

    def get_group_dn(self):
        group_dn = api.portal.get_registry_record(
            'invitation_group_dn', interface=IWorkspaceSettings)
        return group_dn or self._get_orgunit_group_dn()

    def _get_orgunit_group_dn(self):
        """get the dn of the group associated with the current orgunit
        """
        portal = api.portal.get()
        org_units = [ou for ou in get_current_admin_unit().org_units if ou.enabled]
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

        try:
            invitation, payload = self.get_invitation_and_validate_payload()
        except BadRequest:
            self.portal_url = api.portal.get().absolute_url()
            template = ViewPageTemplateFile('templates/invalid_invitation.pt')
            return template(self)

        with elevated_privileges():
            target_workspace = uuidToObject(invitation['target_uuid'])

        if invitation['status'] != STATE_PENDING:
            if not api.user.is_anonymous():
                return self.request.RESPONSE.redirect(target_workspace.absolute_url())
            elif not payload.get("no_redirect"):
                params = {'next': target_workspace.absolute_url()}
                redirect_url = "{}?{}".format(
                    get_gever_portal_url(), urlencode(params))
                return self.request.RESPONSE.redirect(redirect_url)

        if api.user.is_anonymous():
            if payload.get("no_redirect", None):
                # User just registered or logged in on the portal
                # but does not have a GEVER session yet.
                if payload.get("new_user", None):
                    # Make sure new users exist in OGDS which is required when
                    # using OGDS authentication.
                    sync_ogds(
                        api.portal.getSite(),
                        update_remote_timestamps=False,
                    )
                logger.info("Triggering CAS redirect for Anonymous user.")
                raise Unauthorized

            accept_url = "{}/@@my-invitations/accept".format(
                target_workspace.absolute_url())
            accept_params = {'iid': invitation['iid'],
                             'no_redirect': 1}

            if not self.storage()._find_user_id_for_email(invitation['recipient_email']):
                logger.info("Redirecting to new user registration for "
                            "invitation {}".format(invitation['iid']))
                accept_params['new_user'] = 1
                accept_url = "{}?invitation={}".format(
                    accept_url, serialize_and_sign_payload(accept_params))
                group_dn = self.get_group_dn()

                params = {'email': invitation['recipient_email'],
                          'callback': accept_url,
                          'group': group_dn
                          }
                payload = serialize_and_sign_payload(params)
                redirect_url = "{}/registration?invitation={}".format(
                    get_gever_portal_url(), payload)

            else:
                logger.info("E-Mail address for invitation {} matched an existing "
                            "user. Redirecting to portal login.".format(
                                invitation['iid']))

                accept_url = "{}?invitation={}".format(
                    accept_url, serialize_and_sign_payload(accept_params))
                params = {'next': accept_url}
                redirect_url = "{}?{}".format(
                    get_gever_portal_url(), urlencode(params))

            return self.request.RESPONSE.redirect(redirect_url)

        logger.info("Accepting invitation {} for user {!r}".format(
            invitation['iid'], api.user.get_current().getId()))
        target = self._accept(invitation)
        return self.request.RESPONSE.redirect(target.absolute_url())

    def _accept(self, invitation):
        with elevated_privileges():
            target = uuidToObject(invitation['target_uuid'])
            self.storage().map_email_to_current_userid_for_all_invitations(
                invitation['recipient_email'])
            # recipient was set in the invitation, so we need to fetch it anew
            invitation = self.storage().get_invitation(invitation['iid'])

            assignment = SharingRoleAssignment(
                invitation['recipient'], [invitation['role']], target)
            RoleAssignmentManager(target).add_or_update_assignment(assignment)
            self.storage().mark_invitation_as_accepted(invitation['iid'])

            manager = WorkspaceWatcherManager(target)
            manager.new_participant_added(invitation['recipient'])

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
