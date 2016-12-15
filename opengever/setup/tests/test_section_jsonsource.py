from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.setup.sections.jsonsource import JSONSourceSection
from opengever.setup.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestJSONSource(FunctionalTestCase):

    def setup_source(self, options, bundle_path=None, previous=None):
        previous = previous or []
        bundle_path = bundle_path or resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')
        transmogrifier = MockTransmogrifier()
        transmogrifier.bundle_path = bundle_path

        options.setdefault('blueprint', 'opengever.setup.jsonsource')

        return JSONSourceSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(JSONSourceSection))
        verifyClass(ISection, JSONSourceSection)

        self.assertTrue(ISectionBlueprint.providedBy(JSONSourceSection))
        verifyObject(ISectionBlueprint, JSONSourceSection)
