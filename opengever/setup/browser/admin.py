from datetime import datetime
from ftw.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from opengever.setup.interfaces import IClientConfigurationRegistry
from opengever.setup.ldap_creds import configure_ldap_credentials
from opengever.setup.utils import get_entry_points
from opengever.setup.utils import get_ldap_configs
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
import json
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

    def javascript_src_url(self):
        """returns the url to the javascript. This makes it possible to
        change the URL in debug mode.
        """

        base_url = '/++resource++addclient.js'
        if 1:
            return base_url + '?x=' + str(datetime.now())
        else:
            base_url

    def server_port(self):
        return self.request.get('SERVER_PORT')

    def get_default_mail_domain(self):
        return self.request.get('SERVER_NAME')

    def get_ldap_profiles(self):
        """Returns a list of (name, profile) of ldap GS profiles. They are
        registerd as entrypoints.
        """
        return get_ldap_configs()

    def get_policy_options(self):
        """Returns the options for selecting the policy.
        """

        client_registry = getUtility(IClientConfigurationRegistry)
        return client_registry.list_policies()

    def get_policy_defaults(self):
        """Returns the policy defaults for use in javascript.
        """

        client_registry = getUtility(IClientConfigurationRegistry)
        return 'var policy_configs = %s;' % json.dumps(
            list(client_registry.get_policies()), indent=2)

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
        client_registry = getUtility(IClientConfigurationRegistry)
        config = client_registry.get_policy(policy_id)

        # drop sql tables
        if form.get('first') and config.get('purge_sql'):
            self.drop_sql_tables(session)

        ext_profiles = list(EXTENSION_PROFILES)
        if config.get('base_profile'):
            ext_profiles.append(config.get('base_profile'))

        # create plone site
        site = addPloneSite(
            self.context,
            form['client_id'],
            title=form['title'],
            profile_id=_DEFAULT_PROFILE,
            extension_ids=ext_profiles,
            setup_content=False,
            default_language=config.get('language', 'de-ch'),
        )

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = form['client_id'].decode('utf-8')

        # ldap
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

        if form.get('first') and form.get('import_users'):
            print '===== SYNC LDAP ===='
            # Import LDAP users and groups
            sync_ogds(site)

        if form.get('configsql'):
            # register the client in the ogds
            # is the client already configured? -> delete it
            clients = session.query(OrgUnit).filter_by(
                unit_id=form['client_id']).all()
            if clients:
                session.delete(clients[0])

            # groups must exist
            users_groups = session.query(Group).filter_by(
                groupid=form['group'])
            inbox_groups = session.query(Group).filter_by(
                groupid=form['inbox_group'])

            try:
                users_group = users_groups[0]
            except IndexError:
                raise SetupError("User group '%s' could not be found." %
                                 form['group'])

            try:
                inbox_group = inbox_groups[0]
            except IndexError:
                raise SetupError("Inbox group '%s' could not be found." %
                                 form['inbox_group'])

            active = bool(form.get('active'))

            admin_unit = AdminUnit(
                form['client_id'],
                enabled=active,
                title=form['title'],
                abbreviation=form['title'],
                ip_address=form['ip_address'],
                site_url=form['site_url'],
                public_url=form['public_url'],
            )

            client = OrgUnit(form['client_id'],
                             enabled=active,
                             title=form['title'],
                             admin_unit=admin_unit)

            client.users_group = users_group
            client.inbox_group = inbox_group

            session.add(admin_unit)
            session.add(client)

        # create the admin user in the ogds if he not exist
        # and add it to the specified user_group
        # so we avoid a constraintError in the choice fields

        if session.query(User).filter_by(userid=ADMIN_USER_ID).count() == 0:
            og_admin_user = User(ADMIN_USER_ID, firstname='OG',
                                 lastname='Administrator', active=True)
            session.add(og_admin_user)
        else:
            og_admin_user = session.query(User).filter_by(
                userid=ADMIN_USER_ID).first()
            og_admin_user.active = True

        users_group = session.query(Group).filter_by(
            groupid=form['group']).first()

        if og_admin_user not in users_group.users:
            users_group.users.append(og_admin_user)

        # set the mail domain in the registry
        client_id = form['client_id'].decode('utf-8')
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        proxy.mail_domain = form['mail_domain'].decode('utf-8')
        mail_from_address = self.get_mail_from_address()
        site.manage_changeProperties({'email_from_address': mail_from_address,
                                      'email_from_name': client_id})

        # set global Member role for the client users group
        site.acl_users.portal_role_manager.assignRoleToPrincipal(
            'Member', form['group'])

        # set global Member role for readers group
        if form['reader_group']:
            site.acl_users.portal_role_manager.assignRoleToPrincipal(
                'Member', form['reader_group'])

        # set Role Manager role for rolemanager group
        if form['rolemanager_group']:
            site.acl_users.portal_role_manager.assignRoleToPrincipal(
                'Role Manager', form['rolemanager_group'])

        # provide the repository root for opengever.setup:default
        repository_root = config.get('repository_root')
        if repository_root:
            self.request.set('repository_root', repository_root)

        # import the defaul generic setup profiles if needed
        stool = getToolByName(site, 'portal_setup')
        for profile in config.get('additional_profiles', ()):
            stool.runAllImportStepsFromProfile('profile-%s' % profile)

        # set the site title
        site.manage_changeProperties(title=form['title'])

        # REALLY set the language - the plone4 addPloneSite is really
        # buggy with languages.
        langCP = getAdapter(site, ILanguageSelectionSchema)
        langCP.default_language = 'de-ch'

        # the og_admin_user is not longer used so we set him to inactive
        og_admin_user.active = False

        return 'ok'

    def drop_sql_tables(self, session):
        """Drops sql tables, usually when creating the first client
        """
        for base in SQL_BASES:
            try:
                getattr(base, 'metadata').drop_all(session.bind)
            except NoReferencedTableError:
                pass

    def get_mail_from_address(self):
        email_from_address = 'noreply@opengever.4teamwork.ch'
        for ep in get_entry_points('email_from_address'):
            module = ep.load()
            if getattr(module, 'EMAIL_FROM_ADDRESS', None):
                email_from_address = getattr(module, 'EMAIL_FROM_ADDRESS')

        return email_from_address
