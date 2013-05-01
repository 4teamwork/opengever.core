from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.fti import DexterityFTI, register
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.configuration import xmlconfig


class DocumentLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from opengever import document
        xmlconfig.file('tests.zcml', package=document,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        session = create_session()

        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        _create_example_user(session, portal,
                             TEST_USER_ID,
                             {'firstname': 'Hugo',
                              'lastname': 'Boss',
                              'email': 'hugo@boss.ch'},
                             ('og_mandant1_users',))

        # fix registry
        registry = getUtility(IRegistry)
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'plone'
        registry['ftw.tabbedview.interfaces.ITabbedView.batch_size'] = 50

        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Editor'])

        # test basedocument behavior
        fti = DexterityFTI('BaseDocumentFTI')
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
                         'opengever.document.behaviors.IBaseDocument',
                         )
        fti.schema = 'opengever.document.document.IDocumentSchema'
        portal.portal_types._setObject('BaseDocumentFTI', fti)
        register(fti)

    def tearDown(self):
        super(DocumentLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_DOCUMENT_FIXTURE = DocumentLayer()
OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOCUMENT_FIXTURE, ),
    name="OpengeverDocument:Integration")
