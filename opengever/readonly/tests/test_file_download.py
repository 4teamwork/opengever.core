from ftw.testbrowser import browsing
from opengever.bumblebee.events import PDFDownloadedEvent
from opengever.journal.handlers import DOCUMENT_ADDED_ACTION
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from zope.event import notify
import transaction


class TestFileDownloadInReadOnly(IntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_file_download_journaling_doesnt_cause_readonly_error(self, browser):
        self.login(self.regular_user, browser)

        # Get other potential writes-on-read out of the way.
        # Those are not what we're testing here.
        browser.open(self.document,
                     view='tabbed_view/listing',
                     data={'view_name': 'overview'})
        transaction.commit()

        with ZODBStorageInReadonlyMode():
            browser.find('Download copy').click()
            browser.find('Download').click()
            transaction.commit()

        self.assertEqual(200, browser.status_code)
        self.assertEqual(self.document.file._data, browser.contents)

        self.assertEqual(
            len(self.document.file._data),
            int(browser.headers['Content-Length']))

        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document',
            browser.headers['Content-Type'])

    @browsing
    def test_downloading_doc_pdf_journaling_doesnt_cause_readonly_error(self, browser):
        self.login(self.regular_user, browser)

        # Get other potential writes-on-read out of the way.
        # Those are not what we're testing here.
        transaction.commit()

        with ZODBStorageInReadonlyMode():
            notify(PDFDownloadedEvent(self.document))
            transaction.commit()

        # Last journal entry should be document added, not 'PDF downloaded'
        msg = u'Document added: Vertr\xe4gsentwurf'
        self.assert_journal_entry(self.document, DOCUMENT_ADDED_ACTION, msg)

    @browsing
    def test_downloading_mail_pdf_journaling_doesnt_cause_readonly_error(self, browser):
        self.login(self.regular_user, browser)

        # Get other potential writes-on-read out of the way.
        # Those are not what we're testing here.
        transaction.commit()

        with ZODBStorageInReadonlyMode():
            notify(PDFDownloadedEvent(self.mail_eml))
            transaction.commit()

        # Last journal entry should be document added, not 'PDF downloaded'
        msg = u'Document added: Die B\xfcrgschaft'
        self.assert_journal_entry(self.mail_eml, DOCUMENT_ADDED_ACTION, msg)
