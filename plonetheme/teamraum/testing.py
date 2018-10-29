from ftw.builder import Builder
from ftw.builder import create
from ftw.builder.testing import set_builder_session_factory
from opengever.core.testing import functional_session_factory
from opengever.core.testing import OPENGEVER_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import plonetheme.teamraum


class TeamraumThemeFunctionalLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        self.loadZCML('configure.zcml', package=plonetheme.teamraum)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonetheme.teamraum:default')


PLONETHEME_TEAMRAUM_FIXTURE = TeamraumThemeFunctionalLayer()
PLONETHEME_TEAMRAUM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONETHEME_TEAMRAUM_FIXTURE, set_builder_session_factory(functional_session_factory)),
    name="plonetheme.teamraum:functional"
)


class TeamraumThemeTestCase(TestCase):

    layer = PLONETHEME_TEAMRAUM_FUNCTIONAL_TESTING

    def setUp(self):
        super(TeamraumThemeTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        create(Builder('admin_unit').as_current_admin_unit())
