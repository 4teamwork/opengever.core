from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.builder import Builder
from ftw.builder import create
from opengever.setup.sections.fileloader import FileLoaderSection
from opengever.setup.sections.jsonsource import BUNDLE_PATH_KEY
from opengever.setup.sections.jsonsource import JSON_STATS_KEY
from opengever.setup.tests import MockTransmogrifier
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestFileLoader(FunctionalTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        self.transmogrifier = MockTransmogrifier()
        self.transmogrifier.context = api.portal.get()

        self.bundle_path = resource_filename(
            'opengever.setup.tests', 'assets/oggbundle')
        IAnnotations(self.transmogrifier)[BUNDLE_PATH_KEY] = self.bundle_path
        IAnnotations(self.transmogrifier)[JSON_STATS_KEY] = {'errors': {}}
        options = {'blueprint': 'opengever.setup.fileloader'}

        return FileLoaderSection(self.transmogrifier, '', options, previous)

    def test_implements_interface(self):
        self.assertTrue(ISection.implementedBy(FileLoaderSection))
        verifyClass(ISection, FileLoaderSection)

        self.assertTrue(ISectionBlueprint.providedBy(FileLoaderSection))
        verifyObject(ISectionBlueprint, FileLoaderSection)

    def test_loads_file_into_existing_document(self):
        doc = create(Builder('document').titled('Foo Bar'))
        self.assertIsNone(doc.file)
        relative_path = '/'.join(doc.getPhysicalPath()[2:])
        item = {
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
            u"_object": doc,
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('Lorem Ipsum\n', doc.file.data)
        self.assertEqual('application/pdf', doc.file.contentType)
        self.assertEqual('foo-bar.pdf', doc.file.filename)

    def test_syncs_title_from_filename_if_untitled(self):
        doc = create(Builder('document').titled(None))
        self.assertIsNone(doc.file)
        relative_path = '/'.join(doc.getPhysicalPath()[2:])
        item = {
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
            u"_object": doc,
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('beschluss.pdf', doc.file.filename)
        self.assertEqual('beschluss', doc.title)

    def test_tracks_missing_files_in_stats(self):
        item = {
            u"_type": u"opengever.document.document",
            u"_path": '/relative/path/to/doc',
            u"filepath": u"files/missing.file",
        }
        section = self.setup_section(previous=[item])
        list(section)

        stats = IAnnotations(self.transmogrifier)[JSON_STATS_KEY]
        abs_filepath = '/'.join((self.bundle_path, 'files/missing.file'))
        self.assertEqual(
            {abs_filepath: '/relative/path/to/doc'},
            stats['errors']['files_not_found'])

    def test_tracks_skipped_msg_files_in_stats(self):
        item = {
            u"_type": u"opengever.document.document",
            u"_path": '/relative/path/to/doc',
            u"filepath": u"files/outlook.msg",
        }
        section = self.setup_section(previous=[item])
        list(section)

        stats = IAnnotations(self.transmogrifier)[JSON_STATS_KEY]
        abs_filepath = '/'.join((self.bundle_path, 'files/outlook.msg'))
        self.assertEqual(
            {abs_filepath: '/relative/path/to/doc'},
            stats['errors']['msgs'])
