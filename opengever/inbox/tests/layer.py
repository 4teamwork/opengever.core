from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.utils import create_session
from Products.PloneTestCase.setup import portal_owner
from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from opengever.globalindex import model

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever import inbox
        self.loadZCML('configure.zcml', package=inbox)
        from opengever.ogds import base
        self.loadZCML('tests.zcml', package=base)
        from opengever import document
        self.loadZCML('configure.zcml', package=document)
        from opengever import task
        self.loadZCML('configure.zcml', package=task)

        # Install the opengever.inbox product
        self.addProfile('opengever.inbox:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.task:default')
        

        # setup the sql tables for ogds.base and globalindex
        create_sql_tables()
        session = create_session()

        model.Base.metadata.create_all(session.bind)

        _create_example_client(session, 'client1',
                              {'title': 'client1',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        _create_example_client(session, 'client2',
                            {'title': 'client2',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://nohost/plone',
                            'public_url': 'http://nohost/plone',
                            'group': 'og_mandant2_users',
                            'inbox_group': 'og_mandant2_inbox'})

        _create_example_user(session, self.portal, portal_owner,{
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test.user@local.ch',
            'email2': 'test_user@private.ch'},
            ('og_mandant1_users','og_mandant1_inbox'))

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'client1'
          

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])