from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.utils import create_session
from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc


ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever import inbox
        self.loadZCML('configure.zcml', package=inbox)
        from opengever.ogds import base
        self.loadZCML('tests.zcml', package=base)

        # Install the opengever.inbox product
        self.addProfile('opengever.inbox:default')

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