from Products.CMFPlone.browser.admin import AddPloneSite
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from datetime import datetime
from opengever.mail.interfaces import IMailSettings
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.ldap_import import sync_ldap
from opengever.ogds.base.model.client import Client
from opengever.ogds.base.utils import create_session
from opengever.setup.utils import get_ldap_configs, get_policy_configs
from plone.app.controlpanel.language import ILanguageSelectionSchema
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
from zope.publisher.browser import BrowserView
import json
import opengever.globalindex.model
import opengever.ogds.base.model
from sqlalchemy.exc import NoReferencedTableError


SQL_BASES = (
    opengever.ogds.base.model.user.Base,
    opengever.ogds.base.model.client.Base,
    opengever.globalindex.model.Base,
    )


# these profiles will be installed automatically
EXTENSION_PROFILES = (
    'plonetheme.classic:default',
    'plonetheme.sunburst:default',
    )



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

        if form.get('configsql'):
            # register the client in the ogds
            # is the client already configured? -> delete it
            clients = session.query(Client).filter_by(
                client_id=form['client_id']).all()
            if clients:
                session.delete(clients[0])

            client = Client(form['client_id'],
                            title=form['title'],
                            ip_address=form['ip_address'],
                            site_url=form['site_url'],
                            public_url=form['public_url'],
                            # TODO
                            # group=form['group'],
                            # inbox_group=form['inbox_group']
                            )
            session.add(client)


        # set the client id in the registry
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = form['client_id'].decode('utf-8')

        # provide the repository root for opengever.setup:default
        repository_root = config.get('repository_root', None)
        if repository_root:
            self.request.set('repository_root', repository_root)

        # import the defaul generic setup profiles if needed
        stool = getToolByName(site, 'portal_setup')
        for profile in config.get('additional_profiles', ()):
            stool.runAllImportStepsFromProfile('profile-%s' % profile)

        # ldap
        if form.get('ldap', False):
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
            class Object(object): pass
            options = Object()
            options.config = u'opengever.ogds.base.user-import'
            options.site_root = '/' + form['client_id']
            sync_ldap.run_import(self.context, options)

        # set the site title
        site.manage_changeProperties(title=form['title'])

        # set the client id in the registry
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        proxy.mail_domain = form['mail_domain'].decode('utf-8')

        # REALLY set the language - the plone4 addPloneSite is really
        # buggy with languages.
        langCP = getAdapter(site, ILanguageSelectionSchema)
        langCP.default_language = 'de-ch'

        return 'ok'

    def drop_sql_tables(self, session):
        """Drops sql tables, usually when creating the first client
        """
        for base in SQL_BASES:
            try:
                getattr(base, 'metadata').drop_all(session.bind)
            except NoReferencedTableError:
                pass
