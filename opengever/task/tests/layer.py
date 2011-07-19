from ftw.tabbedview.interfaces import ITabbedView
from opengever.globalindex import model
from opengever.ogds.base.setuphandlers import create_sql_tables
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.registry.interfaces import IRegistry
from Products.PloneTestCase import ptc
from Products.PloneTestCase.setup import portal_owner
from zope.component import getUtility
import collective.testcaselayer.ptc

ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever.ogds import base
        self.loadZCML('tests.zcml', package=base)
        from opengever import task
        self.loadZCML('configure.zcml', package=task)
        from opengever import document
        self.loadZCML('configure.zcml', package=document)
        from ftw import tabbedview
        self.loadZCML('configure.zcml', package=tabbedview)
        
        # Install the opengever.task product
        self.addProfile('opengever.task:default')

        self.addProfile('ftw.tabbedview:default')
        self.addProfile('opengever.document:default')

        # setup the sql tables for ogds.base and globalindex
        create_sql_tables()
        session = create_session()

        model.Base.metadata.create_all(session.bind)

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        tab_reg = registry.forInterface(ITabbedView)
        tab_reg.batch_size = 5

        _create_example_client(session, 'plone',
                              {'title': 'plone',
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
            ('og_mandant1_users','og_mandant1_inbox', 'og_mandant2_users'))

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
