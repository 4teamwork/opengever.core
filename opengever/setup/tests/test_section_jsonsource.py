from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from jsonschema.exceptions import ValidationError
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
            'opengever.setup.tests', 'assets')
        transmogrifier = MockTransmogrifier()
        transmogrifier.bundle_path = bundle_path

        options.setdefault('blueprint', 'opengever.setup.jsonsource')

        return JSONSourceSection(transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(JSONSourceSection))
        verifyClass(ISection, JSONSourceSection)

        self.assertTrue(ISectionBlueprint.providedBy(JSONSourceSection))
        verifyObject(ISectionBlueprint, JSONSourceSection)

    def test_skips_missing_files(self):
        directory = resource_filename('opengever.setup.tests', 'nope')
        source = self.setup_source({'bundle_path': directory,
                                    'filename': 'nope.json'},
                                   previous=['Foo'])

        self.assertEqual(['Foo'], list(source))

    def test_json_file_parsing(self):
        source = self.setup_source({'filename': 'simple.json'})
        self.assertEqual(
            [{u'_source': 'simple.json', u'item': u'b\xe4r'}], list(source)
        )

    def test_inserts_portal_type_if_specified(self):
        source = self.setup_source(
            {'filename': 'simple.json',
             'portal_type': 'foo.bar.qux'})
        self.assertEqual(
            [{u'item': u'b\xe4r',
              u'_source': 'simple.json',
              u'_type': 'foo.bar.qux'}],
            list(source)
        )

    def test_validates_portal_type_schema_if_in_supported_types(self):
        source = self.setup_source(
            {'filename': 'reporoot.json',
             'portal_type': 'opengever.repository.repositoryroot'})
        self.assertEqual([{
            '_source': 'reporoot.json',
            '_type': 'opengever.repository.repositoryroot',
            'guid': '754daf80623f45659004a8c38c78dc3e',
            'review_state': 'repositoryroot-state-active',
            'title_de': 'Ordnungssystem',
            'valid_from': '2000-01-01',
            'valid_until': '2099-12-31',
            }],
            list(source))

    def test_validation_fails_when_files_does_not_meet_schema_spec(self):
        source = self.setup_source(
            {'filename': 'simple.json',
             'portal_type': 'opengever.repository.repositoryroot'})
        with self.assertRaises(ValidationError):
            list(source)
