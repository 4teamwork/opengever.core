from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer



class InboxLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE,)

    def tearDown(self):
        super(InboxLayer, self).tearDown()
        truncate_sql_tables()

OPENGEVER_INBOX_FIXTURE = InboxLayer()
OPENGEVER_INBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_INBOX_FIXTURE,), name="OpengeverInbox:Integration")
OPENGEVER_INBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_INBOX_FIXTURE,), name="OpengeverInbox:Functional")
