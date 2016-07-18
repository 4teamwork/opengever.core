from ftw.builder import Builder
from ftw.builder import create
from opengever.bumblebee.events import PDFDownloadedEvent
from opengever.core.testing import activate_bumblebee_feature
from opengever.core.testing import deactivate_bumblebee_feature
from opengever.journal.handlers import PDF_DOWNLOADED
from opengever.testing import FunctionalTestCase
from zope.event import notify


class TestBumblebeeJournal(FunctionalTestCase):

    def setUp(self):
        activate_bumblebee_feature()
        super(TestBumblebeeJournal, self).setUp()

    def tearDown(self):
        super(TestBumblebeeJournal, self).tearDown()
        deactivate_bumblebee_feature()

    def test_downloading_document_pdf_is_journalized(self):
        document = create(Builder('document')
                          .titled(u'Testdocument')
                          .with_asset_file(u'text.txt'))

        notify(PDFDownloadedEvent(document))

        self.assert_journal_entry(document, PDF_DOWNLOADED, u'PDF downloaded')

    def test_downloading_mail_pdf_is_journalized(self):
        mail = create(Builder('mail').with_dummy_message())

        notify(PDFDownloadedEvent(mail))

        self.assert_journal_entry(mail, PDF_DOWNLOADED, u'PDF downloaded')
