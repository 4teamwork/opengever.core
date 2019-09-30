from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.builder import Builder
from ftw.builder import create
from opengever.bundle.loader import BundleLoader
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.fileloader import FileLoaderSection
from opengever.bundle.tests import MockTransmogrifier
from opengever.mail.mail import IOGMail
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
import json


class TestFileLoader(FunctionalTestCase):

    def setup_section(self, previous=None):
        previous = previous or []
        self.transmogrifier = MockTransmogrifier()
        self.transmogrifier.context = api.portal.get()

        self.bundle_path = resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')
        self.bundle = BundleLoader(self.bundle_path).load()
        IAnnotations(self.transmogrifier)[BUNDLE_PATH_KEY] = self.bundle_path
        IAnnotations(self.transmogrifier)[BUNDLE_KEY] = self.bundle
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
            u"guid": u"12345",
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('Lorem Ipsum\n', doc.file.data)
        self.assertEqual('application/pdf', doc.file.contentType)
        self.assertEqual('Foo Bar.pdf', doc.file.filename)

    def test_syncs_title_from_filename_if_untitled(self):
        doc = create(Builder('document').titled(None))
        self.assertIsNone(doc.file)
        relative_path = '/'.join(doc.getPhysicalPath()[2:])
        item = {
            u"guid": u"12345",
            u"_type": u"opengever.document.document",
            u"_path": relative_path,
            u"filepath": u"files/beschluss.pdf",
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual('beschluss.pdf', doc.file.filename)
        self.assertEqual('beschluss', doc.title)

    def test_tracks_missing_files_in_errors(self):
        mail = create(Builder('mail'))
        item = {
            u"guid": u"12345",
            u"_type": u"opengever.document.document",
            u"_path": '/'.join(mail.getPhysicalPath()[2:]),
            u"filepath": u"files/missing.file",
        }
        section = self.setup_section(previous=[item])
        list(section)

        abs_filepath = '/'.join((self.bundle_path, 'files/missing.file'))
        self.assertEqual(
            [(u'12345', abs_filepath, 'document-1')],
            self.bundle.errors['files_not_found'])

    def test_tracks_unmapped_unc_files_in_errors(self):
        mail = create(Builder('mail'))
        item = {
            u"guid": u"12345",
            u"_type": u"opengever.document.document",
            u"_path": '/'.join(mail.getPhysicalPath()[2:]),
            u"filepath": u'\\\\host\\unmapped\\foo.docx',
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(
            set([(u'\\\\host\\unmapped', )]),
            self.bundle.errors['unmapped_unc_mounts'])

        self.assertEqual(
            [(u'12345', item['filepath'], 'document-1')],
            self.bundle.errors['files_unresolvable_path'])

    def test_translates_unc_paths(self):
        section = self.setup_section(previous=[])

        ingestion_settings = {
            u'unc_mounts': {
                u'\\\\server\\share': u'/mnt/mountpoint'}
        }
        # Shove ingestion settings through JSON deserialization to be as
        # close as possible to the real thing (unicode strings!).
        ingestion_settings = json.loads(json.dumps(ingestion_settings))
        section.bundle.ingestion_settings = ingestion_settings

        filepath = '\\\\server\\share\\folder\\b\xc3\xa4rengraben.txt'

        translated_path = section._translate_unc_path(filepath)
        self.assertIsInstance(translated_path, str)
        self.assertEqual(
            '/mnt/mountpoint/folder/b\xc3\xa4rengraben.txt',
            translated_path)

    def test_handles_eml_mails(self):
        mail = create(Builder('mail'))
        self.assertIsNone(mail.message)
        relative_path = '/'.join(mail.getPhysicalPath()[2:])
        item = {
            u"guid": u"12345",
            u"_type": u"ftw.mail.mail",
            u"_path": relative_path,
            u"filepath": u"files/sample.eml",
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(u'Lorem Ipsum', mail.title)
        self.assertEqual(920, len(mail.message.data))
        self.assertEqual('message/rfc822', mail.message.contentType)
        self.assertEqual('Lorem Ipsum.eml', mail.message.filename)
        self.assertEqual(True, mail.digitally_available)

    def test_handles_msg_mails(self):
        mail = create(Builder('mail'))
        self.assertIsNone(mail.message)
        relative_path = '/'.join(mail.getPhysicalPath()[2:])
        item = {
            u"guid": u"12345",
            u"_type": u"ftw.mail.mail",
            u"_path": relative_path,
            u"filepath": u"files/sample.eml",
            u"original_message_path": u"files/sample.msg",
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(
            u'sample.msg', IOGMail(mail).original_message.filename)
        self.assertEqual(13824, len(IOGMail(mail).original_message.data))
        self.assertEqual(u'Lorem Ipsum', mail.title)

    def test_handles_msg_only_mails(self):
        mail = create(Builder('mail'))
        self.assertIsNone(mail.message)
        relative_path = '/'.join(mail.getPhysicalPath()[2:])
        item = {
            u"guid": u"12345",
            u"_type": u"ftw.mail.mail",
            u"_path": relative_path,
            u"filepath": u"files/sample.msg",
        }
        section = self.setup_section(previous=[item])
        list(section)

        self.assertEqual(
            u'sample.msg', IOGMail(mail).original_message.filename)
        self.assertEqual(13824, len(IOGMail(mail).original_message.data))

        self.assertEqual('message/rfc822', mail.message.contentType)
        self.assertEqual(u'Test attachment.eml', mail.message.filename)

    def test_uses_subject_as_title_only_when_no_title_is_given(self):
        mail2 = create(Builder('mail').titled(u'Test Mail'))
        item = {
            u"guid": u"12345",
            u"_type": u"ftw.mail.mail",
            u"_path": '/'.join(mail2.getPhysicalPath()[2:]),
            u"filepath": u"files/sample.eml",
            u"title": 'Test Mail',
        }
        section = self.setup_section(previous=[item])
        list(section)
        self.assertEqual(u'Test Mail', mail2.title)
