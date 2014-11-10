from AccessControl.interfaces import IRoleManager
from ftw.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.ogds.models import BASE
from opengever.setup import DEVELOPMENT_USERS_GROUP
from opengever.setup.ldap_creds import configure_ldap_credentials
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from sqlalchemy.exc import NoReferencedTableError
from zope.component import getAdapter
from zope.component import getUtility
import opengever.globalindex.model


# these profiles will be installed automatically
EXTENSION_PROFILES = (
    'plonetheme.classic:default',
    'plonetheme.sunburst:default',
)


SQL_BASES = (BASE, opengever.globalindex.model.Base)


class GeverDeployment(object):

    def __init__(self, context, config, db_session,
                 is_development_setup=False,
                 has_purge_sql=False,
                 ldap_profile=None,
                 has_ldap_user_import=False):
        self.context = context
        self.config = config
        self.db_session = db_session
        self.is_development_setup = is_development_setup
        self.has_purge_sql = has_purge_sql
        self.ldap_profile = ldap_profile
        self.has_ldap_user_import = has_ldap_user_import

    def create(self):
        self.prepare_sql()
        self.site = self.setup_plone_site()

        self.setup_ldap()
        self.import_ldap_users()
        self.configure_admin_unit()
        self.install_policy_profile()
        self.configure_plone_site()
        self.install_additional_profiles()

        if self.is_development_setup:
            self.configure_development_options()

    def prepare_sql(self):
        if not self.has_purge_sql:
            return

        self.drop_sql_tables(self.db_session)

    def setup_plone_site(self):
        config = self.config
        ext_profiles = list(EXTENSION_PROFILES)
        ext_profiles.append(config['base_profile'])

        return addPloneSite(
            self.context,
            config['admin_unit_id'].encode('utf-8'),
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

        # disable source_groups when using ldap
        for ptype in plugins.listPluginTypeInfo():
            try:
                plugins.deactivatePlugin(ptype['interface'],
                                         'source_groups')
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

    def import_ldap_users(self):
        if not self.has_ldap_user_import:
            return

        print '===== SYNC LDAP ===='
        # Import LDAP users and groups
        sync_ogds(self.site)
        print '===== Done SYNCING LDAP ===='

    def configure_admin_unit(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = self.config['admin_unit_id'].decode('utf-8')

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
                                  'reader_group', 'Member')
        self.assign_group_to_role(self.site, self.config,
                                  'rolemanager_group', 'Role Manager')
        self.assign_group_to_role(self.site, self.config,
                                  'administrator_group', 'Administrator')

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
            if IRoleManager.providedBy(obj):
                obj.manage_addLocalRoles(
                    DEVELOPMENT_USERS_GROUP,
                    ["Contributor", "Editor", "Reader"])

    def drop_sql_tables(self, session):
        """Drops all sql tables, usually for a dev-setup.
        """
        for base in SQL_BASES:
            try:
                getattr(base, 'metadata').drop_all(session.bind)
            except NoReferencedTableError:
                pass
