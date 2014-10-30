from AccessControl.interfaces import IRoleManager
from datetime import datetime
from ftw.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from opengever.setup import DEVELOPMENT_USERS_GROUP
from opengever.setup.interfaces import IDeploymentConfigurationRegistry
from opengever.setup.interfaces import ILDAPConfigurationRegistry
from opengever.setup.ldap_creds import configure_ldap_credentials
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.admin import AddPloneSite
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from sqlalchemy.exc import NoReferencedTableError
from zope.component import getAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView
import App.config
import opengever.globalindex.model


SQL_BASES = (BASE, opengever.globalindex.model.Base)


class SetupError(Exception):
    """An Error happened during OpenGever setup.
    """


# these profiles will be installed automatically
EXTENSION_PROFILES = (
    'plonetheme.classic:default',
    'plonetheme.sunburst:default',
)

ADMIN_USER_ID = 'ogadmin'


class AddOpengeverClient(AddPloneSite):

    default_extension_profiles = EXTENSION_PROFILES

    def __call__(self):
        return self.index()

    def server_port(self):
        return self.request.get('SERVER_PORT')

    def javascript_src_url(self):
        """returns the url to the javascript. This makes it possible to
        change the URL in debug mode.
        """

        base_url = '/++resource++addclient.js'
        return base_url + '?x=' + str(datetime.now())

    def get_ldap_profiles(self):
        """Returns a list of (name, profile) of ldap GS profiles.
        """
        ldap_registry = getUtility(ILDAPConfigurationRegistry)
        return ldap_registry.list_ldaps()

    def get_deployment_options(self):
        client_registry = getUtility(IDeploymentConfigurationRegistry)
        return client_registry.list_deployments()

    def get_ogds_config(self):
        """Returns the DSN URL for the OGDS DB connection currently being
        used.
        """
        session = create_session()
        engine = session.bind
        return "%s" % engine.url

    def get_zodb_config(self):
        """Returns information about the ZODB configuration.
        """
        db_info = ""
        conf = App.config.getConfiguration()
        main_db = [db for db in conf.databases if db.name == 'main'][0]
        storage_cfg = main_db.config.storage.config
        section_type = storage_cfg.getSectionType()

        if section_type == 'relstorage':
            adapter_cfg = storage_cfg.adapter.config
            backend_type = adapter_cfg._matcher.type.name
            dsn = adapter_cfg.dsn
            user = adapter_cfg.user
            db_info = "%s (%s): %s @%s" % (
                section_type, backend_type, user, dsn)
        else:
            # blobstorage
            db_info = "%s" % section_type
        return db_info


class CreateOpengeverClient(BrowserView):

    def __call__(self):
        form = self.request.form
        session = create_session()

        policy_id = form['policy']
        client_registry = getUtility(IDeploymentConfigurationRegistry)
        config = client_registry.get_deployment(policy_id)

        is_development_setup = form.get('dev_mode', False)
        if is_development_setup:
            self.request['unit_creation_dev_mode'] = True

        self.prepare_sql(form, session)
        site = self.setup_plone_site(config)

        self.setup_ldap(site, form)
        self.import_ldap_users(site, form)
        self.configure_admin_unit(config)
        self.install_policy_profile(site, config)
        self.configure_plone_site(site, form, config)
        self.install_additional_profiles(site, config)

        if is_development_setup:
            self.configure_development_options(site)

    def prepare_sql(self, form, session):
        if form.get('purge_sql'):
            self.drop_sql_tables(session)

    def setup_plone_site(self, config):
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

    def setup_ldap(self, site, form):
        stool = getToolByName(site, 'portal_setup')
        if form.get('ldap'):
            stool = getToolByName(site, 'portal_setup')
            stool.runAllImportStepsFromProfile('profile-%s' % form.get('ldap'))

            # Configure credentials from JSON file at
            # ~/.opengever/ldap/{hostname}.json
            configure_ldap_credentials(site)

            acl_users = getToolByName(site, 'acl_users')
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

    def import_ldap_users(self, site, form):
        if not form.get('import_users'):
            return

        print '===== SYNC LDAP ===='
        # Import LDAP users and groups
        sync_ogds(site)

    def configure_admin_unit(self, config):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = config['admin_unit_id'].decode('utf-8')

    def install_policy_profile(self, site, config):
        # import the defaul generic setup profiles if needed
        policy_profile = config.get('policy_profile')
        stool = getToolByName(site, 'portal_setup')
        stool.runAllImportStepsFromProfile(
            'profile-%s' % policy_profile)

    def configure_plone_site(self, site, form, config):
        # set the mail domain in the registry
        client_id = config['title']  # XXX
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        proxy.mail_domain = config['mail_domain'].decode('utf-8')
        site.manage_changeProperties(
            {'email_from_address': config['mail_from_address'],
             'email_from_name': client_id})

        # set global Member role for the client users group
        # site.acl_users.portal_role_manager.assignRoleToPrincipal(
        #     'Member', form['group'])

        # set global Member role for readers group
        if form.get('reader_group'):
            site.acl_users.portal_role_manager.assignRoleToPrincipal(
                'Member', form['reader_group'])

        # set Role Manager role for rolemanager group
        if form.get('rolemanager_group'):
            site.acl_users.portal_role_manager.assignRoleToPrincipal(
                'Role Manager', form['rolemanager_group'])

        # set the site title
        site.manage_changeProperties(title=config['title'])

        # REALLY set the language - the plone4 addPloneSite is really
        # buggy with languages.
        langCP = getAdapter(site, ILanguageSelectionSchema)
        langCP.default_language = 'de-ch'

    def install_additional_profiles(self, site, config):
        # import the defaul generic setup profiles if needed
        additional_profiles = config.get('additional_profiles')
        stool = getToolByName(site, 'portal_setup')
        if additional_profiles:
            for additional_profile in additional_profiles:
                stool.runAllImportStepsFromProfile(
                    'profile-%s' % additional_profile)

    def configure_development_options(self, site):
        for obj in site.listFolderContents():
            if IRoleManager.providedBy(obj):
                obj.manage_addLocalRoles(
                    DEVELOPMENT_USERS_GROUP,
                    ["Contributor", "Editor", "Reader"])

    def drop_sql_tables(self, session):
        """Drops sql tables, usually when creating the first client
        """
        for base in SQL_BASES:
            try:
                getattr(base, 'metadata').drop_all(session.bind)
            except NoReferencedTableError:
                pass
