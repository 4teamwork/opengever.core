from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer


class DossierLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def tearDown(self):
        super(DossierLayer, self).tearDown()
        truncate_sql_tables()

OPENGEVER_DOSSIER_FIXTURE = DossierLayer()
OPENGEVER_DOSSIER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_DOSSIER_FIXTURE, ), name="OpengeverDossier:Integration")
OPENGEVER_DOSSIER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOSSIER_FIXTURE, ), name="OpengeverDossier:Functional")
