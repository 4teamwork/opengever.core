from AccessControl.interfaces import IRoleManager
from ftw.mail.interfaces import IMailSettings
from ftw.solr.browser.maintenance import SolrMaintenanceView
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.contact.interfaces import IContactFolder
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.inbox.container import IInboxContainer
from opengever.inbox.inbox import IInbox
from opengever.meeting.committeecontainer import ICommitteeContainer
from opengever.ogds.auth.admin_unit import addAdminUnitAuthenticationPlugin
from opengever.ogds.auth.plugin import install_ogds_auth_plugin
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.setup import DEVELOPMENT_USERS_GROUP
from opengever.setup.ldap_creds import configure_ldap_credentials
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from sqlalchemy import MetaData
from zope.component import getAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest


# these profiles will be installed automatically
EXTENSION_PROFILES = (
    'plonetheme.classic:default',
    'plonetheme.sunburst:default',
)

# these profiles must always be installed in that order
BASE_PROFILES = (
    'opengever.core:default',
    'plonetheme.teamraum:gever',
    'opengever.policy.base:mimetype',
)

POLICYLESS_SITE_ID = 'ogsite'


class GeverDeployment(object):

    def __init__(self, context, config, db_session,
                 is_development_setup=False,
                 has_purge_sql=False,
                 has_purge_solr=False,
                 ldap_profile=None,
                 has_ogds_sync=False):
        self.context = context
        self.config = config
        self.db_session = db_session
        self.is_development_setup = is_development_setup
        self.is_policyless = config.get('is_policyless', False)
        self.has_purge_sql = has_purge_sql
        self.has_purge_solr = has_purge_solr
        self.ldap_profile = ldap_profile
        self.has_ogds_sync = has_ogds_sync

    def create(self):
        self.prepare_sql()
        self.prepare_solr()
        self.site = self.setup_plone_site()

        self.setup_ldap()
        self.setup_ogds_auth_plugin()
        self.sync_ogds()
        self.configure_admin_unit()
        self.install_policy_profile()
        self.configure_plone_site()
        self.install_additional_profiles()
        self.install_admin_unit_auth_plugin()

        if self.is_development_setup:
            self.configure_development_options()

    def prepare_sql(self):
        if not self.has_purge_sql:
            return

        self.drop_sql_tables(self.db_session)

    def prepare_solr(self):
        if not self.has_purge_solr:
            return
        SolrMaintenanceView(self.context, getRequest()).clear(force=True)

    def setup_plone_site(self):
        config = self.config
        ext_profiles = list(EXTENSION_PROFILES)
        ext_profiles.extend(BASE_PROFILES)

        if self.is_policyless:
            # For policyless deployments, admin unit will be set up later,
            # and the Plone site ID won't be tied to it.
            plone_site_id = POLICYLESS_SITE_ID
        else:
            plone_site_id = config.get('admin_unit_id').encode('utf-8')

        return addPloneSite(
            self.context,
            plone_site_id,
            title=config['title'],
            profile_id=_DEFAULT_PROFILE,
            extension_ids=ext_profiles,
            setup_content=False,
            default_language=config.get('language', 'de-ch'),
        )

    def setup_ldap(self):
        if not self.ldap_profile:
            return

        stool = getToolByName(self.site, 'portal_setup')
        stool = getToolByName(self.site, 'portal_setup')
        stool.runAllImportStepsFromProfile(
            'profile-{0}'.format(self.ldap_profile))

        # Configure credentials from JSON file at
        # ~/.opengever/ldap/{hostname}.json
        configure_ldap_credentials(self.site)

        acl_users = getToolByName(self.site, 'acl_users')
        plugins = acl_users.plugins

        # disable source_groups when using ldap except for group management,
        # enumeration, introspection and groups lookup which are used to create
        # groups over the @groups endpoint and use it for local roles.
        for ptype in plugins.listPluginTypeInfo():
            if ptype['id'] in ['IGroupEnumerationPlugin',
                               'IGroupIntrospection',
                               'IGroupsPlugin']:
                continue
            if ptype['id'] == 'IGroupManagement':
                to_deactivate = 'ldap'
            else:
                to_deactivate = 'source_groups'
            try:
                plugins.deactivatePlugin(ptype['interface'],
                                         to_deactivate)
            except KeyError:
                pass

        # deactivate recursive groups
        for ptype in plugins.listPluginTypeInfo():
            try:
                plugins.deactivatePlugin(ptype['interface'],
                                         'recursive_groups')
            except KeyError:
                pass

        # move ldap up
        plugins.movePluginsUp(IPropertiesPlugin, ('ldap',))
        plugins.movePluginsUp(IPropertiesPlugin, ('ldap',))
        plugins.movePluginsUp(IPropertiesPlugin, ('ldap',))

        if not self.is_development_setup:
            # Deactivate 'Authentication' capability for LDAP plugin
            # In production, auth will always be performed by CAS portal
            try:
                plugins.deactivatePlugin(IAuthenticationPlugin, 'ldap')
            except KeyError:
                pass

    def setup_ogds_auth_plugin(self):
        if self.is_policyless:
            install_ogds_auth_plugin()

    def install_admin_unit_auth_plugin(self):
        # This plugin can only be installed if the admin unit already exists
        # in OGDS which is not the case for policyless installations.
        if not self.is_policyless:
            addAdminUnitAuthenticationPlugin(
                None, 'admin_unit_auth', 'Admin Unit Authentication Plugin')

    def sync_ogds(self):
        if not self.has_ogds_sync or self.is_policyless:
            # TODO: Disable "Sync OGDS" checkbox in setup form for policyless
            # deployments, since it won't have an effect.
            return

        print '===== SYNC LDAP ===='
        # Import LDAP users and groups
        sync_ogds(self.site)
        print '===== Done SYNCING LDAP ===='

    def configure_admin_unit(self):
        """With classic installations, the admin unit will be created during
        Plone site setup, and the registry  `current_unit_id` will be
        set accordingly. The admin unit's ID will be used as the Plone site ID
        as well.

        In policyless setup style however, the admin unit ID should be omitted
        from the registerDeployment directive, since it will be created later.
        """
        admin_unit_id = self.config.get('admin_unit_id')

        if admin_unit_id:
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IAdminUnitConfiguration)
            proxy.current_unit_id = admin_unit_id.decode('utf-8')

    def install_policy_profile(self):
        # import the default generic setup profiles if needed
        policy_profile = self.config.get('policy_profile')
        stool = getToolByName(self.site, 'portal_setup')
        stool.runAllImportStepsFromProfile(
            'profile-{}'.format(policy_profile))

    def configure_plone_site(self):
        # configure mail settings
        site_title = self.config['title']
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        proxy.mail_domain = self.config['mail_domain'].decode('utf-8')
        self.site.manage_changeProperties(
            {'email_from_address': self.config['mail_from_address'],
             'email_from_name': site_title})
        # set the site title
        self.site.manage_changeProperties(title=site_title)

        self.assign_group_to_role(self.site, self.config,
                                  'reader_group', 'Reader')
        self.assign_group_to_role(self.site, self.config,
                                  'rolemanager_group', 'Role Manager')
        self.assign_group_to_role(self.site, self.config,
                                  'administrator_group', 'Administrator')
        self.assign_group_to_role(self.site, self.config,
                                  'limited_admin_group', 'Administrator')
        self.assign_group_to_role(self.site, self.config,
                                  'archivist_group', 'Archivist')
        self.assign_group_to_role(self.site, self.config,
                                  'records_manager_group', 'Records Manager')
        self.assign_group_to_role(self.site, self.config,
                                  'api_group', 'APIUser')
        self.assign_group_to_role(self.site, self.config,
                                  'workspace_client_user_group',
                                  'WorkspaceClientUser')
        self.assign_group_to_role(self.site, self.config,
                                  'workspace_user_group', 'WorkspacesUser')
        self.assign_group_to_role(self.site, self.config,
                                  'workspace_creator_group', 'WorkspacesCreator')

        # REALLY set the language - the plone4 addPloneSite is really
        # buggy with languages.
        langCP = getAdapter(self.site, ILanguageSelectionSchema)
        langCP.default_language = 'de-ch'

    def assign_group_to_role(self, site, config, group_name_key, role_name):
        group_name = config.get(group_name_key)
        if not group_name:
            return

        site.acl_users.portal_role_manager.assignRoleToPrincipal(
            role_name, group_name)

    def install_additional_profiles(self):
        additional_profiles = self.config.get('additional_profiles')
        stool = getToolByName(self.site, 'portal_setup')
        if additional_profiles:
            for additional_profile in additional_profiles:
                stool.runAllImportStepsFromProfile(
                    'profile-%s' % additional_profile)

    def configure_development_options(self):
        for obj in self.site.listFolderContents():
            if not IRoleManager.providedBy(obj):
                continue

            if self._has_default_role_assignments(obj):
                self._assign_roles_to_development_users_group(
                    ["Contributor", "Editor", "Reader"], obj)
            elif self._has_meeting_role_assignments(obj):
                self._assign_roles_to_development_users_group(
                    ["CommitteeAdministrator"], obj)

    def _assign_roles_to_development_users_group(self, roles, obj):
        assignment = SharingRoleAssignment(DEVELOPMENT_USERS_GROUP, roles)
        RoleAssignmentManager(obj).add_or_update_assignment(assignment)

    def _has_default_role_assignments(self, obj):
        return any([
            IRepositoryRoot.providedBy(obj),
            IInbox.providedBy(obj),
            IInboxContainer.providedBy(obj),
            ITemplateFolder.providedBy(obj),
            IContactFolder.providedBy(obj),
        ])

    def _has_meeting_role_assignments(self, obj):
        return ICommitteeContainer.providedBy(obj)

    def drop_sql_tables(self, session):
        """Drops all sql tables, usually for a dev-setup.
        """
        temp_metadata = MetaData(bind=session.bind)
        temp_metadata.reflect()
        temp_metadata.drop_all()
