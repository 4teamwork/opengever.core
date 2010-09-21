from Products.PloneTestCase import ptc
from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.client import Client
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import collective.testcaselayer.ptc


ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.document product
        self.addProfile('opengever.document:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class CheckoutTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        from Products.Five import zcml
        import opengever.document
        zcml.load_config('tests.zcml', opengever.document)
        import opengever.ogds.base
        zcml.load_config('test.zcml', opengever.ogds.base)
        # Install the opengever.document product
        self.addProfile('opengever.dossier:default')
        self.addProfile('opengever.ogds.base:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.document:tests')
        import opengever.base
        zcml.load_config('configure.zcml', opengever.base)
        # fix registry
        registry = getUtility(IRegistry)
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'm1'

        # create a client for testing
        create_sql_tables()
        client = Client(u'm1',
                        title=u'Mandant 1',
                        enabled=True,
                        public_url=u'http://nohost/plone',
                        site_url=u'http://nohost/plone',
                        ip_address=u'127.0.0.1')
        session = create_session()
        session.add(client)

    def beforeTearDown(self):
        # drop sql stuff
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)


CLayer = CheckoutTestLayer([collective.testcaselayer.ptc.ptc_layer])
