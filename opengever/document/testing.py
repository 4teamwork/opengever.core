from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class DocumentLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        session = create_session()

        _create_example_user(session, portal,
                             TEST_USER_ID,
                             {'firstname': 'Hugo',
                              'lastname': 'Boss',
                              'email': 'hugo@boss.ch'},
                             ('og_mandant1_users',))

        # fix registry
        registry = getUtility(IRegistry)
        registry['ftw.tabbedview.interfaces.ITabbedView.batch_size'] = 50

    def tearDown(self):
        super(DocumentLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_DOCUMENT_FIXTURE = DocumentLayer()
OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOCUMENT_FIXTURE, ),
    name="OpengeverDocument:Integration")
