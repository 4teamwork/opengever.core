from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.loader import Bundle
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.bundlesource import BundleSourceSection
from opengever.bundle.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestBundleSource(FunctionalTestCase):

    def setup_source(self, options, bundle_path=None, previous=None):
        previous = previous or []
        bundle_path = bundle_path or resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')
        transmogrifier = MockTransmogrifier()
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = bundle_path

        options.setdefault('blueprint', 'opengever.bundle.bundlesource')

        return BundleSourceSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(BundleSourceSection))
        verifyClass(ISection, BundleSourceSection)

        self.assertTrue(ISectionBlueprint.providedBy(BundleSourceSection))
        verifyObject(ISectionBlueprint, BundleSourceSection)

    def test_yields_items_from_bundle(self):
        source = self.setup_source({})
        self.assertEqual(16, len(list(source)))

    def test_raises_if_bundle_path_missing(self):
        transmogrifier = MockTransmogrifier()
        with self.assertRaises(Exception):
            BundleSourceSection(transmogrifier, '', {}, [])

    def test_adds_reference_to_bundle_to_transmogrifier(self):
        source = self.setup_source({})
        self.assertIsInstance(
            IAnnotations(source.transmogrifier)[BUNDLE_KEY], Bundle)
