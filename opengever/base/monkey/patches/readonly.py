from AccessControl.ImplPython import ZopeSecurityPolicy
from ftw.casauth.plugin import CASAuthenticationPlugin
from opengever.base.monkey.patching import MonkeyPatch
from opengever.readonly import is_in_readonly_mode
from plone.app.contentrules import handlers as contentrules_handlers
from plone.protect import subscribers as plone_protect_subscribers
from plone.protect.interfaces import IDisableCSRFProtection
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.membership import MembershipTool
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides


class PatchMembershipToolSetLoginTimes(MonkeyPatch):
    """In read-only mode, allow login of existing users without updating
    their last login times (which would cause a write).

    The return value of False signals that this is not the user's very
    first login.
    """

    def __call__(self):

        def setLoginTimes(self):
            if is_in_readonly_mode():
                return False

            return original_setLoginTimes(self)

        locals()['__patch_refs__'] = False
        original_setLoginTimes = MembershipTool.setLoginTimes

        self.patch_refs(MembershipTool, 'setLoginTimes', setLoginTimes)


class PatchCASAuthSetLoginTimes(MonkeyPatch):
    """Same for ftw.casauth - don't update last login times in readonly mode.
    """

    def __call__(self):

        def set_login_times(self, member):
            if is_in_readonly_mode():
                return False

            return original_set_login_times(self, member)

        locals()['__patch_refs__'] = False
        original_set_login_times = CASAuthenticationPlugin.set_login_times

        self.patch_refs(CASAuthenticationPlugin, 'set_login_times', set_login_times)


class PatchContentRulesHandlerOnLogin(MonkeyPatch):
    """In read-only mode, don't execute the plone.app.contentrules handler
    on the UserLoggedInEvent. This handler may in some cases initialize some
    settings on the Plone site, and would therefore cause writes.
    """

    def __call__(self):

        def user_logged_in(event):
            if is_in_readonly_mode():
                return

            return original_user_logged_in(event)

        locals()['__patch_refs__'] = False
        original_user_logged_in = contentrules_handlers.user_logged_in

        self.patch_refs(contentrules_handlers, 'user_logged_in', user_logged_in)


class PatchPloneProtectOnUserLogsIn(MonkeyPatch):
    """In read-only mode, prevent plone.protect from rotating the key ring on
    login, which may cause DB writes and prevent the user from logging in.
    """

    def __call__(self):

        @adapter(IUserLoggedInEvent)
        def onUserLogsIn(event):
            if is_in_readonly_mode():
                # disable csrf protection on login requests
                req = getRequest()
                alsoProvides(req, IDisableCSRFProtection)
                return

            return original_onUserLogsIn(event)

        locals()['__patch_refs__'] = False
        original_onUserLogsIn = plone_protect_subscribers.onUserLogsIn

        self.patch_refs(plone_protect_subscribers, 'onUserLogsIn', onUserLogsIn)


class PatchMembershipToolCreateMemberarea(MonkeyPatch):
    """In read-only mode, don't create a user's member area.

    This would cause a DB write and therefore is not supported while readonly
    mode is active.
    """

    def __call__(self):

        def createMemberarea(self, *args, **kwargs):
            if is_in_readonly_mode():
                return

            return original_createMemberarea(self, *args, **kwargs)

        locals()['__patch_refs__'] = False
        original_createMemberarea = MembershipTool.createMemberarea

        # Patch both spellings (API change in CMF)
        self.patch_refs(MembershipTool, 'createMemberarea', createMemberarea)
        self.patch_refs(MembershipTool, 'createMemberArea', createMemberarea)


# Roles strongly associated with write operations

WRITER_ROLES = [
    'Contributor',
    'Editor',
    'PrivilegedNotificationDispatcher',
    'PropertySheetsManager',
    'Publisher',
    'Reviewer',
    'Role Manager',
    'WorkspacesCreator',
]


class PatchPloneUserAllowed(MonkeyPatch):
    """In order to deactivate most functionality that would cause writes
    during read-only mode, like adding or editing content, we filter the
    roles that the user has during RO mode.

    As a first line of "defense", we do this by patching PloneUser.allowed
    in a way that it doesn't consider those filtered roles as giving the
    permission that is currently being checked for.
    """

    def __call__(self):

        def allowed(self, object, object_roles=None):
            if is_in_readonly_mode():
                if object_roles is not None:
                    object_roles = [r for r in object_roles if r not in WRITER_ROLES]

            return original_allowed(self, object, object_roles=object_roles)

        locals()['__patch_refs__'] = False
        original_allowed = PloneUser.allowed

        self.patch_refs(PloneUser, 'allowed', allowed)


class PatchPloneUserGetRolesInContext(MonkeyPatch):
    """Patch PloneUser.getRolesInContext to filter out roles that the user
    appears to have.

    This is mainly required to deactivate workflow transitions, which are
    often protected by guard-roles. Those are compared directly to the roles
    the user has, so we need to filter those as well.
    """

    def __call__(self):

        def getRolesInContext(self, context):
            roles = original_getRolesInContext(self, context)

            if is_in_readonly_mode():
                roles = [r for r in roles if r not in WRITER_ROLES]

            return roles

        locals()['__patch_refs__'] = False
        original_getRolesInContext = PloneUser.getRolesInContext

        self.patch_refs(PloneUser, 'getRolesInContext', getRolesInContext)


WRITE_PERMISSIONS = [
    'Modify portal content',
    'Add portal content',

    'ftw.keywordwidget: Add new term',
    'ftw.mail: Add Inbound Mail',
    'ftw.mail: Add Mail',
    'opengever.contact: Add contact',
    'opengever.contact: Add contactfolder',
    'opengever.contact: Add team',
    'opengever.disposition: Add disposition',
    'opengever.document: Add document',
    'opengever.dossier: Add businesscasedossier',
    'opengever.dossier: Add dossiertemplate',
    'opengever.dossier: Add templatefolder',
    'opengever.inbox: Add Forwarding',
    'opengever.inbox: Add Inbox',
    'opengever.inbox: Add Year Folder',
    'opengever.inbox: Scan In',
    'opengever.meeting: Add Committee',
    'opengever.meeting: Add CommitteeContainer',
    'opengever.meeting: Add Meeting Template',
    'opengever.meeting: Add Paragraph Template',
    'opengever.meeting: Add Period',
    'opengever.meeting: Add Proposal',
    'opengever.meeting: Add Proposal Comment',
    'opengever.meeting: Add Proposal Template',
    'opengever.meeting: Add Sablon Template',
    'opengever.ogds.base: Sync the OGDS',
    'opengever.private: Add private dossier',
    'opengever.private: Add private folder',
    'opengever.private: Add private root',
    'opengever.propertysheets: Manage PropertySheets',
    'opengever.repository: Add repositoryfolder',
    'opengever.repository: Add repositoryroot',
    'opengever.task: Add task',
    'opengever.task: Add task comment',
    'opengever.workspace: Add Workspace',
    'opengever.workspace: Add WorkspaceFolder',
    'opengever.workspace: Add WorkspaceRoot',

    'ftw.tokenauth: Manage own Service Keys',
    'ftw.usermigration: Migrate users',
    'opengever.api: Manage Groups',
    'opengever.api: Manage Role Assignment Reports',
    'opengever.api: Notify Arbitrary Users',
    'opengever.api: Transfer Assignment',
    'opengever.api: Remove any watcher',
    'opengever.contact: Edit team',
    'opengever.disposition: Edit transfer number',
    'opengever.document: Cancel',
    'opengever.document: Checkin',
    'opengever.document: Checkout',
    'opengever.document: Force Checkin',
    'opengever.document: Modify archival file',
    'opengever.dossier: Delete dossier',
    'opengever.dossier: Destroy dossier',
    'opengever.dossier: Protect dossier',
    'opengever.repository: Unlock Reference Prefix',
    'opengever.ris: Add Proposal',
    'opengever.task: Edit task',
    'opengever.trash: Trash content',
    'opengever.trash: Untrash content',
    'opengever.webactions: Manage own WebActions',
    'opengever.workspaceclient: Unlink Workspace',
    'opengever.workspace: Delete Todos',
    'opengever.workspace: Delete Documents',
    'opengever.workspace: Delete Workspace Folders',
    'opengever.workspace: Delete Workspace Meeting Agenda Items',
    'opengever.workspace: Delete Workspace',
    'opengever.workspace: Modify Workspace',
    'opengever.workspace: Update Content Order',

    'Remove GEVER content',
    'Delete objects',
    'Copy or Move',
    'Edit lifecycle and classification',

    'Set own properties',
    'Sharing page: Delegate Role Manager role',
]


class PatchCheckPermission(MonkeyPatch):
    """Patch ZopeSecurityPolicy.checkPermission to filter a user's permissions.

    While filtering roles gets us quite far in automatically deactivating
    functionality that would require write-access to the DB, there's still a
    significant number of write actions that need to be deactivated by
    filtering permissions, instead of just roles.
    """

    def __call__(self):

        def checkPermission(self, permission, object, context):
            if is_in_readonly_mode():
                if permission in WRITE_PERMISSIONS:
                    return 0

            return original_checkPermission(self, permission, object, context)

        locals()['__patch_refs__'] = False
        original_checkPermission = ZopeSecurityPolicy.checkPermission

        self.patch_refs(ZopeSecurityPolicy, 'checkPermission', checkPermission)
