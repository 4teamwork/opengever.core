from contextlib import contextmanager
from datetime import datetime
from ftw.builder import session
from ftw.testing import freeze
from ftw.testing import staticuid
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from opengever.base.interfaces import ISearchSettings
from opengever.base.model import create_session
from opengever.core.solr_testing import SolrReplicationAPIClient
from opengever.core.solr_testing import SolrServer
from opengever.core.testing import OpengeverFixture
from opengever.testing.helpers import incrementing_intids
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest
import imp
import os
import pytz
import transaction


SOLR_PORT = os.environ.get('SOLR_PORT', '55003')
SOLR_CORE = os.environ.get('SOLR_CORE', 'testserver')


class TestserverLayer(OpengeverFixture):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

    def setUpZope(self, app, configurationContext):
        SolrServer.get_instance().configure(SOLR_PORT, SOLR_CORE).start()
        import collective.indexing.monkey  # noqa
        import ftw.solr.patches  # noqa

        super(TestserverLayer, self).setUpZope(app, configurationContext)

        # Solr must be started before registering the connection since ftw.solr
        # will get the schema from solr and cache it.
        SolrServer.get_instance().await_ready()
        xmlconfig.string(
            '<configure xmlns:solr="http://namespaces.plone.org/solr">'
            '  <solr:connection host="localhost"'
            '                   port="{SOLR_PORT}"'
            '                   base="/solr/{SOLR_CORE}" />'
            '</configure>'.format(SOLR_PORT=SOLR_PORT, SOLR_CORE=SOLR_CORE),
            context=configurationContext)

        # Clear solr from potential artefacts of the previous run.
        SolrReplicationAPIClient.get_instance().clear()

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(TestserverLayer, self).setUpPloneSite(portal)

        applyProfile(portal, 'plonetheme.teamraum:gever')

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        api.portal.set_registry_record('use_solr', True, interface=ISearchSettings)

        setRequest(portal.REQUEST)
        print 'Installing fixture. Have patience.'
        self.get_fixture_class()()
        print 'Finished installing fixture.'
        setRequest(None)

        # Commit before creating the solr backup, since collective.indexing
        # flushes on commit.
        transaction.commit()
        SolrReplicationAPIClient.get_instance().create_backup('fixture')

    def setupLanguageTool(self, portal):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        lang_tool.supported_langs = ['de-ch']

    def get_fixture_class(self):
        """The fixture of the testserver should be replaceable from the outside.
        The idea is that the 'FIXTURE' environment variable can be set to a path
        to a python file which is located in another project.
        Therefore we import the file manually in the context of GEVER so that
        subclassing the fixture works.
        """
        custom_fixture_path = os.environ.get('FIXTURE', None)

        if not custom_fixture_path:
            from opengever.testing.fixtures import OpengeverContentFixture
            return OpengeverContentFixture

        fixture_dir = os.path.dirname(custom_fixture_path)
        package_name = 'customfixture'
        module_name = os.path.splitext(os.path.basename(custom_fixture_path))[0]
        module_path = '{}.{}'.format(package_name, module_name)

        # It is important to first load the package of the custom fixture, so that
        # local imports will work within this package.
        imp.load_module(package_name, *imp.find_module('.', [fixture_dir]))
        module = imp.load_module(module_path, *imp.find_module(module_name, [fixture_dir]))
        class_name = os.environ.get('FIXTURE_CLASS', 'Fixture')
        klass = getattr(module, class_name, None)
        assert klass, 'Could not find class {!r} in module {!r}'.format(class_name, module)
        return klass


class TestServerFunctionalTesting(FunctionalTesting):

    @contextmanager
    def isolation(self):
        start = datetime(2018, 11, 22, 14, 29, 33, tzinfo=pytz.UTC)
        with freeze(start, ignore_modules=['ftw.tokenauth.oauth2.jwt_grants']):
            with staticuid('testserver-session'):
                with incrementing_intids():
                    yield

    def testSetUp(self):
        super(TestServerFunctionalTesting, self).testSetUp()
        self.context_manager = self.isolation()
        self.context_manager.__enter__()
        transaction.commit()
        SolrReplicationAPIClient.get_instance().await_restored()

    def testTearDown(self):
        self.context_manager.__exit__(None, None, None)
        SolrReplicationAPIClient.get_instance().restore_backup('fixture')
        super(TestServerFunctionalTesting, self).testTearDown()


OPENGEVER_TESTSERVER = TestServerFunctionalTesting(
    bases=(TestserverLayer(), z2.ZSERVER_FIXTURE),
    name="opengever.core:testserver")
