from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer


class MailIntegrationLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (OPENGEVER_FIXTURE,)

    def tearDown(self):
        super(MailIntegrationLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_MAIL_FIXTURE = MailIntegrationLayer()
OPENGEVER_MAIL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_MAIL_FIXTURE,), name="OpengeverMail:Integration")

OPENGEVER_MAIL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_MAIL_FIXTURE,), name="OpengeverMail:Functional")


class MockEvent(object):

    #History: [[interface, context], ]
    event_history = []

    def mock_handler(self, event):
        self.event_history.append(event, )

    def last_event(self):
        return self.event_history[-1]
