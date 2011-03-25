from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from opengever.globalindex import model as task_model

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

    def beforeTearDown(test):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)
        getattr(task_model.Base, 'metadata').drop_all(session.bind)
        # we may have created custom users and

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
