from contextlib import contextmanager
from datetime import datetime
from ftw.builder import session
from ftw.testing import freeze
from ftw.testing import staticuid
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from opengever.base.model import create_session
from opengever.core.testing import OpengeverFixture
from opengever.testing.helpers import incrementing_intids
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from zope.globalrequest import setRequest
import imp
import os
import pytz
import transaction


class TestserverLayer(OpengeverFixture):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

    def setUpPloneSite(self, portal):
        session.current_session = session.BuilderSession()
        session.current_session.session = create_session()
        super(TestserverLayer, self).setUpPloneSite(portal)

        applyProfile(portal, 'plonetheme.teamraum:gever')

        portal.portal_languages.use_combined_language_codes = True
        portal.portal_languages.addSupportedLanguage('de-ch')

        setRequest(portal.REQUEST)
        print 'Installing fixture. Have patience.'
        self.get_fixture_class()()
        print 'Finished installing fixture.'
        setRequest(None)

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

    def testTearDown(self):
        self.context_manager.__exit__(None, None, None)
        super(TestServerFunctionalTesting, self).testTearDown()


OPENGEVER_TESTSERVER = TestServerFunctionalTesting(
    bases=(TestserverLayer(), z2.ZSERVER_FIXTURE),
    name="opengever.core:testserver")
