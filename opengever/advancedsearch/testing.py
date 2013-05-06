from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer


class BaseLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def tearDown(self):
        super(BaseLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_ADV_SEARCH_FIXTURE = BaseLayer()
OPENGEVER_ADV_SEARCH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_ADV_SEARCH_FIXTURE,), name="OpengeverAdvancedsearch:Functional")
