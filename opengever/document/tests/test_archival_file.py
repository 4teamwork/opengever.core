from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.archival_file import ARCHIVAL_FILE_STATE_CONVERTED
from opengever.document.archival_file import ARCHIVAL_FILE_STATE_MANUALLY
from opengever.document.archival_file import ARCHIVAL_FILE_STATE_CONVERTING
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import FunctionalTestCase


class TestArchivalFile(FunctionalTestCase):

    def setUp(self):
        super(TestArchivalFile, self).setUp()
        self.document = create(Builder('document')
                          .titled(u'\xdcberpr\xfcfung XY')
                          .with_dummy_content())

    @browsing
    def test_archival_file_state_is_omitted(self, browser):
        browser.login().open(self.document, view='edit')

        self.assertEquals(
            [],
            browser.css('#formfield-form-widgets-'
                        'IDocumentMetadata-archival_file_state'))

    def test_file_name_is_file_filename_with_pdf_extension(self):
        self.assertEquals(
            'uberprufung-xy.pdf',
            ArchivalFileConverter(self.document).get_file_name())

    def test_trigger_conversion_sets_state_to_converting(self):
        ArchivalFileConverter(self.document).trigger_conversion()
        self.assertEquals(ARCHIVAL_FILE_STATE_CONVERTING,
                          IDocumentMetadata(self.document).archival_file_state)

    def test_trigger_conversion_skip_files_in_manually_state(self):
        document = create(Builder('document')
                          .titled(u'\xdcberpr\xfcfung XY')
                          .with_dummy_content()
                          .having(archival_file_state=ARCHIVAL_FILE_STATE_MANUALLY))

        ArchivalFileConverter(self.document).trigger_conversion()

        self.assertEquals(ARCHIVAL_FILE_STATE_MANUALLY,
                          IDocumentMetadata(document).archival_file_state)

    def test_store_file_sets_state_to_converted(self):
        ArchivalFileConverter(self.document).store_file('TEST DATA')
        self.assertEquals(
            ARCHIVAL_FILE_STATE_CONVERTED,
            IDocumentMetadata(self.document).archival_file_state)
