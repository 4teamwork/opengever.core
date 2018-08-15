from ftw.builder import Builder
from ftw.builder import create
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.archival_file import STATE_MANUALLY_PROVIDED
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.tests.test_archival_file import TestArchivalFile
from opengever.testing import FunctionalTestCase


class TestArchivalFileForMails(TestArchivalFile):

    def setUp(self):
        FunctionalTestCase.setUp(self)
        self.document = create(Builder('mail')
                               .titled(u'\xdcberpr\xfcfung XY')
                               .with_dummy_message())
        self.grant('Manager')

    def test_trigger_conversion_skip_files_in_manually_state(self):
        document = create(Builder('mail')
                          .titled(u'\xdcberpr\xfcfung XY')
                          .with_dummy_message()
                          .having(archival_file_state=STATE_MANUALLY_PROVIDED))

        ArchivalFileConverter(document).trigger_conversion()

        self.assertEquals(STATE_MANUALLY_PROVIDED,
                          IDocumentMetadata(document).archival_file_state)
