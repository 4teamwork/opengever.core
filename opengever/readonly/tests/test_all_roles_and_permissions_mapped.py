from AccessControl.Permission import getPermissions
from opengever.base.monkey.patches.readonly import WRITE_PERMISSIONS
from opengever.base.monkey.patches.readonly import WRITER_ROLES
from opengever.testing import IntegrationTestCase
from operator import itemgetter
from plone import api
from textwrap import dedent


NON_WRITER_ROLES = [
    'Administrator',
    'Archivist',
    'CommitteeAdministrator',
    'CommitteeMember',
    'CommitteeResponsible',
    'DossierManager',
    'Impersonator',
    'LimitedAdmin',
    'Manager',
    'MeetingUser',
    'Member',
    'MemberAreaAdministrator',
    'Owner',
    'Reader',
    'Records Manager',
    'ServiceKeyUser',
    'Site Administrator',
    'TaskResponsible',
    'WebActionManager',
    'WorkspaceAdmin',
    'WorkspaceClientUser',
    'WorkspaceGuest',
    'WorkspaceMember',
    'WorkspacesUser',
]


NON_WRITE_PERMISSIONS = [
    'Access arbitrary user session data',
    'Access contents information',
    'Access future portal content',
    'Access inactive portal content',
    'Access session data',
    'Access Transient Objects',
    'Add Archetypes Tools',
    'Add ATContentTypes tools',
    'Add CMF Action Icons Tools',
    'Add CMF Caching Policy Managers',
    'Add CMF Calendar Tools',
    'Add CMF Core Tools',
    'Add CMF Default Tools',
    'Add CMF Diff Tools',
    'Add CMF Editions Tools',
    'Add CMF Placeful Workflow Tools',
    'Add CMF QuickInstaller Tools',
    'Add CMF Sites',
    'Add CMF Unique Id Tools',
    'Add CMFQuickInstallerTools',
    'Add Content Type Registrys',
    'Add Controller Page Templates',
    'Add Controller Python Scripts',
    'Add Controller Validators',
    'Add Cookie Crumblers',
    'Add Documents, Images, and Files',
    'Add Filesystem Directory Views',
    'Add Folders',
    'Add Form Controller Tools',
    'Add Generic Setup Tools',
    'Add Groups',
    'Add MimetypesRegistry Tools',
    'Add Password Reset Tools',
    'Add Placeful Workflow Tools',
    'Add Plone Language Tools',
    'Add Plone Tools',
    'Add PlonePAS Tools',
    'Add Pluggable Index',
    'Add Plugin Registrys',
    'Add portal events',
    'Add portal folders',
    'Add portal member',
    'Add portal topics',
    'Add PortalTransforms Tools',
    'Add Python Scripts',
    'Add ResourceRegistries Tools',
    'Add Site Roots',
    'Add TinyMCE Tools',
    'Add User Folders',
    'Add Vocabularies',
    'Add Workflow Policy',
    'Allow sendto',
    'Archetypes Tests: Protected Type View',
    'Archetypes Tests: Protected Type Write',
    'ATContentTypes Topic: Add ATBooleanCriterion',
    'ATContentTypes Topic: Add ATCurrentAuthorCriterion',
    'ATContentTypes Topic: Add ATDateCriteria',
    'ATContentTypes Topic: Add ATDateRangeCriterion',
    'ATContentTypes Topic: Add ATListCriterion',
    'ATContentTypes Topic: Add ATPathCriterion',
    'ATContentTypes Topic: Add ATPortalTypeCriterion',
    'ATContentTypes Topic: Add ATReferenceCriterion',
    'ATContentTypes Topic: Add ATRelativePathCriterion',
    'ATContentTypes Topic: Add ATSelectionCriterion',
    'ATContentTypes Topic: Add ATSimpleIntCriterion',
    'ATContentTypes Topic: Add ATSimpleStringCriterion',
    'ATContentTypes Topic: Add ATSortCriterion',
    'ATContentTypes: Add Document',
    'ATContentTypes: Add Event',
    'ATContentTypes: Add File',
    'ATContentTypes: Add Folder',
    'ATContentTypes: Add Image',
    'ATContentTypes: Add Large Plone Folder',
    'ATContentTypes: Add Link',
    'ATContentTypes: Add News Item',
    'ATContentTypes: Upload via url',
    'ATContentTypes: View history',
    'Change bindings',
    'Change Browser Id Manager',
    'Change cache managers',
    'Change cache settings',
    'Change configuration',
    'Change Database Methods',
    'Change DTML Documents',
    'Change DTML Methods',
    'Change External Methods',
    'Change Images and Files',
    'Change local roles',
    'Change Lock Information',
    'Change Page Templates',
    'Change permissions',
    'Change portal events',
    'Change portal topics',
    'Change proxy roles',
    'Change Python Scripts',
    'Change Session Data Manager',
    'Change user folder',
    'CMFEditions: Access previous versions',
    'CMFEditions: Apply version control',
    'CMFEditions: Checkout to location',
    'CMFEditions: Manage versioning policies',
    'CMFEditions: Purge version',
    'CMFEditions: Revert to previous versions',
    'CMFEditions: Save new version',
    'CMFPlacefulWorkflow: Manage workflow policies',
    'Content rules: Manage rules',
    'Create Transient Objects',
    'Define permissions',
    'Delete Groups',
    'Edit comments',
    'Edit date of cassation',
    'Edit date of submission',
    'Five: Add TTW View Template',
    'FTP access',
    'ftw.tokenauth: Impersonate user',
    'Import/Export objects',
    'iterate : Check in content',
    'iterate : Check out content',
    'List folder contents',
    'List portal members',
    'List undoable changes',
    'Log Site Errors',
    'Log to the Event Log',
    'Mail forgotten password',
    'Manage Five local sites',
    'Manage Groups',
    'Manage portal',
    'Manage properties',
    'Manage repositories',
    'Manage schemata',
    'Manage Site',
    'Manage Transient Object Container',
    'Manage users',
    'Manage Vocabulary',
    'Manage WebDAV Locks',
    'Manage ZCatalog Entries',
    'Manage ZCatalogIndex Entries',
    'Modify constrain types',
    'Modify Cookie Crumblers',
    'Modify view template',
    'opengever.api: Access error log',
    'opengever.api: View AllowedRolesAndPrincipals',
    'opengever.bumblebee: Revive Preview',
    'opengever.disposition: Download SIP Package',
    'opengever.meeting: Add Member',
    'opengever.repository: Export repository',
    'opengever.sign: Sign Document',
    'opengever.sharing: List Protected Objects',
    'opengever.workspace: Access all users and groups',
    'opengever.workspace: Manage Workspaces',
    'opengever.workspaceclient: Use Workspace Client',
    'opengever.workspace: Access hidden members',
    'Plone Site Setup: Calendar',
    'Plone Site Setup: Editing',
    'Plone Site Setup: Filtering',
    'Plone Site Setup: Imaging',
    'Plone Site Setup: Language',
    'Plone Site Setup: Mail',
    'Plone Site Setup: Markup',
    'Plone Site Setup: Navigation',
    'Plone Site Setup: Overview',
    'Plone Site Setup: Search',
    'Plone Site Setup: Security',
    'Plone Site Setup: Site',
    'Plone Site Setup: Themes',
    'Plone Site Setup: TinyMCE',
    'Plone Site Setup: Types',
    'Plone Site Setup: Users and Groups',
    'plone.app.blob: Add Blob',
    'plone.app.collection: Add Collection',
    'plone.cachepurging: Manually purge objects',
    'plone.portlet.collection: Add collection portlet',
    'plone.portlet.static: Add static portlet',
    'plone.resource: Export ZIP file',
    'plone.resourceeditor: Manage Sources',
    'plone.restapi: Access Plone user information',
    'plone.restapi: Access Plone vocabularies',
    'plone.restapi: Use REST API',
    'Poi: Edit response',
    'Poi: Modify issue assignment',
    'Poi: Modify issue severity',
    'Poi: Modify issue state',
    'Poi: Modify issue tags',
    'Poi: Modify issue target release',
    'Poi: Modify issue watchers',
    'Poi: Upload attachment',
    'Portlets: Manage own portlets',
    'Portlets: Manage portlets',
    'Portlets: View dashboard',
    'Private, only accessible from trusted code',
    'Public, everyone can access',
    'Query Vocabulary',
    'Reply to item',
    'Request review',
    'Review comments',
    'Review portal content',
    'Search for principals',
    'Search ZCatalog',
    'Set Group Ownership',
    'Set own password',
    'Sharing page: Delegate Administrator role',
    'Sharing page: Delegate CommitteeAdministrator role',
    'Sharing page: Delegate CommitteeMember role',
    'Sharing page: Delegate CommitteeResponsible role',
    'Sharing page: Delegate Contributor role',
    'Sharing page: Delegate DossierManager role',
    'Sharing page: Delegate Editor role',
    'Sharing page: Delegate MeetingUser role',
    'Sharing page: Delegate Publisher role',
    'Sharing page: Delegate Reader role',
    'Sharing page: Delegate Reviewer role',
    'Sharing page: Delegate roles',
    'Sharing page: Delegate TaskResponsible role',
    'Sharing page: Delegate WorkspaceAdmin role',
    'Sharing page: Delegate WorkspaceGuest role',
    'Sharing page: Delegate WorkspaceMember role',
    'Sharing page: Delegate WorkspacesCreator role',
    'Sharing page: Delegate WorkspacesUser role',
    'Take ownership',
    'Undo changes',
    'Use Database Methods',
    'Use external editor',
    'Use mailhost services',
    'Use version control',
    'View Groups',
    'View History',
    'View management screens',
    'View',
    'WebDAV access',
    'WebDAV Lock items',
    'WebDAV Unlock items',
    'opengever.systemmessages: Manage System Messages',
    'opengever.workspace: Export Workspace Participants'
]


class TestAllRolesAndPermissionsMapped(IntegrationTestCase):

    def get_roles(self):
        acl_users = api.portal.get_tool('acl_users')
        role_manager = acl_users.portal_role_manager
        role_manager.listRoleInfo()
        return map(itemgetter('id'), role_manager.listRoleInfo())

    def test_writer_roles_and_not_writer_roles_are_disjoint(self):
        intersection = set(WRITER_ROLES).intersection(set(NON_WRITER_ROLES))
        self.assertEqual(
            set(),
            intersection,
            "Each role should be either in WRITER_ROLES or in "
            "NON_WRITER_ROLES. {} are currently in both.".format(intersection))

    def test_all_roles_mapped(self):
        all_roles = self.get_roles()

        for role in all_roles:
            mapped = role in (WRITER_ROLES + NON_WRITER_ROLES)

            if not mapped:
                msg = """\
                Role %r is not mapped with regards to readonly mode:

                Please include this role either in the list of WRITER_ROLES
                in og.base.monkey.patches.readonly, or in the
                NON_WRITER_ROLES list above this test.

                You should include it in WRITER_ROLES if the overwhelming
                majority of actions associated with this role can only work
                with write access to the DB, and it is not a role that
                groups together read- as well as write-permissions.

                It will then be witheld from users in readonly mode in order
                to disable those actions.

                Otherwise, please add it to NON_WRITER_ROLES above.

                If in doubt, add it to NON_WRITER_ROLES. The worst that
                can happen is that the user gets a ReadOnlyError during
                readonly mode because an action was offered to them that
                can't work.

                The other way around we would be depriving them from
                functionality that only requires read access, and *could*
                work in readonly mode.
                """ % role
                self.fail(dedent(msg))

    def test_write_permissions_and_non_write_permissions_are_disjoint(self):
        intersection = set(WRITE_PERMISSIONS).intersection(
            set(NON_WRITE_PERMISSIONS))
        self.assertEqual(
            set(),
            intersection,
            "Each permission should be either in WRITE_PERMISSIONS or in "
            "NON_WRITE_PERMISSIONS. {} are currently in both.".format(intersection))

    def test_all_permissions_mapped(self):
        all_permissions = map(itemgetter(0), getPermissions())

        for permission in all_permissions:
            mapped = permission in (WRITE_PERMISSIONS + NON_WRITE_PERMISSIONS)

            if not mapped:
                msg = """\
                Permission %r is not mapped with regards to readonly mode:

                Please include this permission either in the list of
                WRITE_PERMISSIONS in og.base.monkey.patches.readonly, or
                in the NON_WRITE_PERMISSIONS list above this test.

                You should include it in WRITE_PERMISSIONS if the overwhelming
                majority of actions protected by this permission can only work
                with write access to the DB.

                It will then be witheld from users in readonly mode in order
                to disable those actions.

                Otherwise, please add it to NON_WRITE_PERMISSIONS above.

                If in doubt, add it to NON_WRITE_PERMISSIONS. The worst that
                can happen is that the user gets a ReadOnlyError during
                readonly mode because an action was offered to them that
                can't work.

                The other way around we would be depriving them from
                functionality that only requires read access, and *could*
                work in readonly mode.
                """ % permission
                self.fail(dedent(msg))
