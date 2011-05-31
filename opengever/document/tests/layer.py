from Products.PloneTestCase import ptc
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.client import Client
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import collective.testcaselayer.ptc
from opengever.ogds.base.setuphandlers import _create_example_client

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        from Products.Five import zcml
        import opengever.document
        import opengever.base
        zcml.load_config('tests.zcml', opengever.document)
        zcml.load_config('configure.zcml', opengever.base)
        # Install the opengever.document product
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.ogds.base:default')
        self.addProfile('opengever.base:default')
        self.addProfile('ftw.tabbedview:default')
        # fix registry
        registry = getUtility(IRegistry)
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'plone'
        registry['ftw.tabbedview.interfaces.ITabbedView.batch_size'] = 50


    def testSetUp(self):
        # setup the sql tables
        create_sql_tables()
        session = create_session()

        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
