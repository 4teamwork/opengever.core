from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from Products.PloneTestCase.setup import portal_owner, default_password

from opengever.globalindex import model as task_model
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever.dossier import tests
        self.loadZCML('testing.zcml', package=tests)
        
        # Install the example.conference product
        self.addProfile('opengever.ogds.base:default')
        self.addProfile('opengever.dossier:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.task:default')
        self.addProfile('opengever.mail:default')
        self.addProfile('opengever.tabbedview:default')

        # setup the sql tables
        create_sql_tables()
        session = create_session()
        task_model.Base.metadata.create_all(session.bind)

        _create_example_client(
            session, 'client1',
            {'title': 'Client 1',
             'ip_address': '127.0.0.1',
             'site_url': 'http://nohost/client1',
             'public_url': 'http://nohost/client1',
             'group': 'client1_users',
             'inbox_group': 'client1_inbox_users'})

        _create_example_user(
            session, self.portal,
            portal_owner,
            {'firstname': 'Test',
             'lastname': 'User',
             'email': 'test.user@local.ch',
             'email2': 'test_user@private.ch'},
            ('client1_users',
            'client1_inbox_users'))

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'client1'

    def beforeTearDown(test):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)



        # we may have created custom users and

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
