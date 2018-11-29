from ftw.builder import session
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from opengever.base.model import create_session
from opengever.core.testing import OpengeverFixture
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from zope.globalrequest import setRequest


class TestserverLayer(OpengeverFixture):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(TestserverLayer, self).setUpPloneSite(portal)

        applyProfile(portal, 'plonetheme.teamraum:gever')

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        from opengever.testing.fixtures import OpengeverContentFixture
        setRequest(portal.REQUEST)
        print 'Installing fixture. Have patience.'
        OpengeverContentFixture()()
        print 'Finished installing fixture.'
        setRequest(None)

    def setupLanguageTool(self, portal):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        lang_tool.supported_langs = ['de-ch']

    def testSetUp(self):
        super(TestserverLayer, self).testSetUp()
        print 'TEST SET UP'

    def testTearDown(self):
        super(TestserverLayer, self).testTearDown()
        print 'TEST TEAR DOWN'


OPENGEVER_TESTSERVER = FunctionalTesting(
    bases=(TestserverLayer(), z2.ZSERVER_FIXTURE),
    name="opengever.core:testerver")
