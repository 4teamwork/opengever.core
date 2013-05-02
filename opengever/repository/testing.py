from opengever.core.testing import OPENGEVER_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class RepositoryLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Member', 'Reviewer', 'Manager'])


OPENGEVER_REPOSITORY_FIXTURE = RepositoryLayer()
OPENGEVER_REPOSITORY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_REPOSITORY_FIXTURE, ),
    name="OpengeverRepository:Functional")
