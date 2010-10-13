from Products.CMFPlone.browser.admin import AddPloneSite
from opengever.ogds.base.ldap_import import sync_ldap
from opengever.ogds.base.model.client import Client
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from zope.publisher.browser import BrowserView
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import getToolByName
from datetime import datetime
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.utils import create_session
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import opengever.globalindex.model
import opengever.ogds.base.model


SQL_BASES = (
    opengever.ogds.base.model.client.Base,
    opengever.ogds.base.model.user.Base,
    opengever.globalindex.model.Base,
    )


# these profiles will be installed automatically
EXTENSION_PROFILES = (
    'plonetheme.classic:default',
    'plonetheme.sunburst:default',
    'opengever.policy.base:default',
    )


# these profiles will be installed automatically after setting
# the client id
ADDITIONAL_PROFILES = (
    'opengever.examplecontent:developer',
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


class CreateOpengeverClient(BrowserView):

    def __call__(self):
        form = self.request.form
        session = create_session()

        # drop sql tables
        if form.get('drop_sql_tables'):
            self.drop_sql_tables(session)

        # create plone site
        site = addPloneSite(
            self.context,
            form['client_id'],
            title=form['title'],
            profile_id=_DEFAULT_PROFILE,
            extension_ids=EXTENSION_PROFILES,
            setup_content=False,
            default_language=form['default_language'],
            )

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
                        group=form['group'],
                        inbox_group=form['inbox_group'])
        session.add(client)


        # set the client id in the registry
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = form['client_id'].decode('utf-8')

        # import the defaul generic setup profiles if needed
        stool = getToolByName(site, 'portal_setup')
        if form.get('example', False):
            for profile in ADDITIONAL_PROFILES:
                stool.runAllImportStepsFromProfile('profile-%s' % profile)

        # ldap ?
        acl_users = getToolByName(site, 'acl_users')
        plugins = acl_users.plugins
        if form.get('ldap', False):
            stool.runAllImportStepsFromProfile('profile-%s' % form.get('ldap'))
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

        if form.get('import_users'):
            print '===== SYNC LDAP ===='
            class Object(object): pass
            options = Object()
            options.config = u'opengever.ogds.base.user-import'
            options.site_root = '/' + form['client_id']
            sync_ldap.run_import(self.context, options)

        # set the site title
        site.manage_changeProperties(title=form['title'])


        return 'ok'

    def drop_sql_tables(self, session):
        """Drops sql tables, usually when creating the first client
        """
        for base in SQL_BASES:
            getattr(base, 'metadata').drop_all(session.bind)
