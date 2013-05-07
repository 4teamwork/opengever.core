from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer


class TaskFunctionalLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (OPENGEVER_FIXTURE, )

    def tearDown(self):
        super(TaskFunctionalLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_TASK_FIXTURE = TaskFunctionalLayer()
OPENGEVER_TASK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_TASK_FIXTURE, ),
    name="OpengeverTask:Integration")
OPENGEVER_TASK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASK_FIXTURE, ),
    name="OpengeverTask:Functional")
