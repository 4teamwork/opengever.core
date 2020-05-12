from opengever.bundle.loader import BundleLoader
from opengever.bundle.loader import IngestionSettingsReader
from opengever.bundle.loader import ItemPreprocessor
from opengever.bundle.loader import unicode2bytes
from opengever.bundle.tests.helpers import get_portal_type
from opengever.bundle.tests.helpers import get_title
from pkg_resources import resource_filename as rf
from unittest import TestCase
import collections
import jsonschema
import tempfile


def get_bundle_path(bundle_name):
    return rf('opengever.bundle.tests', 'assets/%s' % bundle_name)


class TestBundleLoader(TestCase):

    def load_bundle(self, bundle_path=None):
        if not bundle_path:
            bundle_path = get_bundle_path('basic.oggbundle')
        loader = BundleLoader(bundle_path)
        bundle = loader.load()
        return bundle

    def test_loads_configuration(self):
        bundle = self.load_bundle()
        self.assertEqual({}, bundle.configuration)

    def test_loads_correct_number_of_items(self):
        bundle = self.load_bundle()
        self.assertEqual(16, len(list(bundle)))

    def test_loads_items_in_correct_order(self):
        bundle = self.load_bundle()
        self.assertEqual(
            [('repositoryroot', 'Ordnungssystem'),
             ('repositoryfolder', 'Personal'),
             ('repositoryfolder', 'Organigramm, Prozesse'),
             ('repositoryfolder', 'Organisation'),
             ('businesscasedossier', 'Dossier Peter Schneider'),
             ('businesscasedossier',
              'Dossier in bestehendem Examplecontent Repository'),
             ('businesscasedossier', 'Hanspeter M\xc3\xbcller'),
             ('document', 'Bewerbung Hanspeter M\xc3\xbcller'),
             ('document', 'Entlassung Hanspeter M\xc3\xbcller'),
             ('mail', 'Ein Mail'),
             ('mail', ''),
             ('document', 'Document referenced via UNC-Path'),
             ('document', 'Nonexistent document referenced via UNC-Path with Umlaut'),
             ('document', 'Dokument in bestehendem Examplecontent Dossier'),
             ('mail', 'Mail in bestehendem Examplecontent Dossier'),
             ('mail', 'Signiertes Mail.')],
            [(get_portal_type(i), get_title(i)) for i in list(bundle)])

    def test_loaded_items_contain_bytestrings(self):
        def fail_if_unicode(data):
            if isinstance(data, str):
                return
            elif isinstance(data, unicode):
                self.fail("Data contains unicode string")
            elif isinstance(data, collections.Mapping):
                map(fail_if_unicode, data.iteritems())
            elif isinstance(data, collections.Iterable):
                map(fail_if_unicode, data)

        bundle = self.load_bundle()
        fail_if_unicode(list(bundle))

    def test_inserts_portal_type(self):
        bundle = self.load_bundle()
        self.assertEqual([
            ('businesscasedossier', 'Dossier Peter Schneider'),
            ('businesscasedossier',
             'Dossier in bestehendem Examplecontent Repository'),
            ('businesscasedossier', 'Hanspeter M\xc3\xbcller'),
            ('document', 'Bewerbung Hanspeter M\xc3\xbcller'),
            ('document', 'Document referenced via UNC-Path'),
            ('document', 'Dokument in bestehendem Examplecontent Dossier'),
            ('document', 'Entlassung Hanspeter M\xc3\xbcller'),
            ('document', 'Nonexistent document referenced via UNC-Path with Umlaut'),
            ('mail', ''),
            ('mail', 'Ein Mail'),
            ('mail', 'Mail in bestehendem Examplecontent Dossier'),
            ('mail', 'Signiertes Mail.'),
            ('repositoryfolder', 'Organigramm, Prozesse'),
            ('repositoryfolder', 'Organisation'),
            ('repositoryfolder', 'Personal'),
            ('repositoryroot', 'Ordnungssystem')],
            sorted([(get_portal_type(i), get_title(i)) for i in list(bundle)]))

    def test_validates_schemas(self):
        bundle_path = get_bundle_path('schema_violation.oggbundle')

        with self.assertRaises(jsonschema.ValidationError):
            self.load_bundle(bundle_path)

    def test_skips_missing_files_gracefully(self):
        bundle = self.load_bundle(get_bundle_path('partial.oggbundle'))
        self.assertEqual(1, len(list(bundle)))


class TestItemPreprocessor(TestCase):

    def test_strips_extension_from_title(self):
        item = {'title': 'foo.txt', 'filepath': '/file1.txt'}
        ItemPreprocessor(item, 'documents.json').process()
        self.assertEqual('foo', item['title'])

    def test_strips_extension_from_title_but_keeps_original_filename(self):
        item = {'title': 'foo.txt', 'filepath': '/file1.txt'}
        ItemPreprocessor(item, 'documents.json').process()
        self.assertEqual('foo.txt', item['_original_filename'])

    def test_doesnt_strip_non_extension(self):
        item = {'title': 'Position 1.2.3', 'filepath': '/file1.txt'}
        ItemPreprocessor(item, 'documents.json').process()
        self.assertEqual('Position 1.2.3', item['title'])

    def test_sets_portal_type_based_on_json_name_by_default(self):
        item = {}
        ItemPreprocessor(item, 'reporoots.json').process()
        expected = 'opengever.repository.repositoryroot'
        self.assertEqual(expected, item['_type'])

        item = {}
        ItemPreprocessor(item, 'repofolders.json').process()
        expected = 'opengever.repository.repositoryfolder'
        self.assertEqual(expected, item['_type'])

        item = {}
        ItemPreprocessor(item, 'dossiers.json').process()
        expected = 'opengever.dossier.businesscasedossier'
        self.assertEqual(expected, item['_type'])

        item = {'filepath': 'regular_document.docx', 'title': ''}
        ItemPreprocessor(item, 'documents.json').process()
        expected = 'opengever.document.document'
        self.assertEqual(expected, item['_type'])

    def test_sets_portal_type_for_mails(self):
        item = {'filepath': 'mail.eml', 'title': ''}
        ItemPreprocessor(item, 'documents.json').process()
        expected = 'ftw.mail.mail'
        self.assertEqual(expected, item['_type'])

    def test_drops_review_state_for_items_with_one_state_workflows(self):
        item = {
            'title': 'My document',
            'filepath': '/mydoc.docx',
            'review_state': 'document-state-draft'
        }
        ItemPreprocessor(item, 'documents.json').process()
        self.assertNotIn('review_state', item)


class TestIngestionSettingsReader(TestCase):

    def setUp(self):
        super(TestIngestionSettingsReader, self).setUp()

    def test_loads_settings_from_json_file(self):
        with tempfile.NamedTemporaryFile() as settings_file:
            settings_file.write('{}')
            settings_file.flush()

            reader = IngestionSettingsReader(settings_file.name)
            settings = reader()
            self.assertEqual({}, settings)

    def test_doesnt_fail_if_settings_file_doesnt_exist(self):
        reader = IngestionSettingsReader('/missing/directory/file.json')
        settings = reader()
        self.assertEqual({}, settings)


class TestUnicode2Bytes(TestCase):

    def test_unicode_string(self):
        self.assertEqual('foo', unicode2bytes(u'foo'))
        self.assertTrue(isinstance(unicode2bytes(u'foo'), str))

    def test_byte_string(self):
        self.assertEqual('foo', unicode2bytes('foo'))
        self.assertTrue(isinstance(unicode2bytes('foo'), str))

    def test_list(self):
        data = unicode2bytes([
            u'foo',
            u'bar',
        ])
        self.assertEqual(['foo', 'bar'], data)
        for item in data:
            self.assertTrue(isinstance(item, str))

    def test_dict(self):
        data = unicode2bytes({
            u'foo': u'bar',
            u'spam': u'eggs',
        })
        self.assertEqual({'foo': 'bar', 'spam': 'eggs'}, data)
        for k, v in data.items():
            self.assertTrue(isinstance(k, str))
            self.assertTrue(isinstance(v, str))

    def test_nested(self):
        data = unicode2bytes({
            u'foo': {
                u'bar': [u'baz', u'qux'],
            },
        })
        self.assertEqual({'foo': {'bar': ['baz', 'qux']}}, data)
        self.assertTrue(isinstance(data.keys()[0], str))
        self.assertTrue(isinstance(data['foo'].keys()[0], str))
        for item in data['foo']['bar']:
            self.assertTrue(isinstance(item, str))
