from opengever.core.testing import OPENGEVER_FIXTURE
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from plone.app.testing import PloneSandboxLayer


class TrashLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE,)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])


OPENGEVER_TRASH_FIXTURE = TrashLayer()
OPENGEVER_TRASH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_TRASH_FIXTURE,), name="OpengeverTrash:Integration")
