from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer


class TaskTemplatesLayer(PloneSandboxLayer):
    defaultBases = (OPENGEVER_FIXTURE, )

    def testTearDown(self):
        super(TaskTemplatesLayer, self).testTearDown()
        truncate_sql_tables()


OPENGEVER_TASKTEMPLATES_FIXTURE = TaskTemplatesLayer()
OPENGEVER_TASKTEMPLATES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASKTEMPLATES_FIXTURE, ),
    name="OpengeverTaskTemplates:Functional")
