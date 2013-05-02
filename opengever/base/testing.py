from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.utils import create_session
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class BaseLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE,)

    def setUpPloneSite(self, portal):
        session = create_session()
        _create_example_client(session, 'plone',
                              {'title': 'Plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'

        # Disable the prevent_deletion subscriber. In tests, we WANT
        # to be able to quickly delete objs without becoming Manager
        from opengever.base import subscribers
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.unregisterHandler(subscribers.prevent_deletion)

    def tearDown(self):
        super(BaseLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_BASE_FIXTURE = BaseLayer()
OPENGEVER_BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_BASE_FIXTURE,), name="OpengeverBase:Integration")


class IEmptySchema(form.Schema):
    """an empty schema used or tests"""
