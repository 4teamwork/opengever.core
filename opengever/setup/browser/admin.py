from Products.CMFPlone.browser.admin import AddPloneSite
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from datetime import datetime
from opengever.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.ldap_import import sync_ldap
from opengever.ogds.base.utils import create_session
from opengever.ogds.models import BASE
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.setup.utils import get_ldap_configs, get_policy_configs, get_entry_points
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.registry.interfaces import IRegistry
from sqlalchemy.exc import NoReferencedTableError
from zope.component import getAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView
import json
import opengever.globalindex.model


SQL_BASES = (
    BASE,
    opengever.globalindex.model.Base,
    )


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
        for policy in get_policy_configs():
            yield {'title': policy['title'],
                   'value': policy['id']}

    def get_policy_defaults(self):
        """Returns the policy defaults for use in javascript.
        """
        return 'var policy_configs = %s;' % json.dumps(list(get_policy_configs()), indent=2)


class CreateOpengeverClient(BrowserView):

    def __call__(self):
        form = self.request.form
        session = create_session()

        policy_id = form['policy']
        config = filter(lambda cfg:cfg['id'] == policy_id,
                        get_policy_configs())[0]

        # drop sql tables
        if form.get('first', False) and config.get('purge_sql', False):
            self.drop_sql_tables(session)

        ext_profiles = list(EXTENSION_PROFILES)
        if config.get('base_profile', None):
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
        
        # ldap
        stool = getToolByName(site, 'portal_setup')
        if form.get('ldap', False):
            stool = getToolByName(site, 'portal_setup')
            stool.runAllImportStepsFromProfile('profile-%s' % form.get('ldap'))

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

        if form.get('first', False) and form.get('import_users', False):
            print '===== SYNC LDAP ===='

            #user import
            class Object(object): pass
            options = Object()
            options.config = u'opengever.ogds.base.user-import'
            options.site_root = '/' + form['client_id']
            options.update_syncstamp = False
            sync_ldap.run_import(self.context, options)

            #group import
            options.config = u'opengever.ogds.base.group-import'
            sync_ldap.run_import(self.context, options)

        if form.get('configsql'):
            # register the client in the ogds
            # is the client already configured? -> delete it
            clients = session.query(Client).filter_by(
                client_id=form['client_id']).all()
            if clients:
                session.delete(clients[0])

            # groups must exist
            users_group = session.query(Group).filter_by(groupid=form['group'])[0]
            inbox_group = session.query(Group).filter_by(groupid=form['inbox_group'])[0]

            active = bool(form.get('active', False))

            client = Client(form['client_id'],
                            enabled=active,
                            title=form['title'],
                            ip_address=form['ip_address'],
                            site_url=form['site_url'],
                            public_url=form['public_url'],
                            )

            client.users_group = users_group
            client.inbox_group = inbox_group

            session.add(client)

        # create the admin user in the ogds if he not exist
        # and add it to the specified user_group
        # so we avoid a constraintError in the choice fields

        if session.query(User).filter_by(userid=ADMIN_USER_ID).count() == 0:
            og_admin_user = User(ADMIN_USER_ID, firstname='OG',
                        lastname='Administrator', active=True)
            session.add(og_admin_user)
        else:
            og_admin_user = session.query(User).filter_by(userid=ADMIN_USER_ID).first()
            og_admin_user.active = True

        users_group = session.query(Group).filter_by(groupid=form['group']).first()
        if og_admin_user not in users_group.users:
            users_group.users.append(og_admin_user)

        # set the client id in the registry
        client_id = form['client_id'].decode('utf-8')
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = form['client_id'].decode('utf-8')

        # set the mail domain in the registry
        mail_domain = form['mail_domain'].decode('utf-8')
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        proxy.mail_domain = form['mail_domain'].decode('utf-8')
        mail_name = self.get_mail_name()
        site.manage_changeProperties({'email_from_address': mail_name+'@'+mail_domain,
                                    'email_from_name': client_id})
        
        # provide the repository root for opengever.setup:default
        repository_root = config.get('repository_root', None)
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
    
    
    def get_mail_name(self):
        mail_name = 'noreply'
        import pdb; pdb.set_trace( )
        for ep in get_entry_points('mail_name'):
            module = ep.load()
            if getattr(module, 'MAIL_NAME', None):
                mail_name = getattr(module, 'MAIL_NAME')

        return mail_name
    