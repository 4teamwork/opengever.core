from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.locking.interfaces import IRefreshableLockable


class TestDocumentQuickupload(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentQuickupload, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_upload_box_is_hidden_when_document_is_not_checked_out(self, browser):
        document = create(Builder('document').within(self.dossier))

        browser.login().open(document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_hidden_when_document_is_locked(self, browser):
        document = create(Builder('document').within(self.dossier))
        IRefreshableLockable(document).lock()

        browser.login().open(document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_shown_when_document_is_checked_out_and_not_locked(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .checked_out())

        browser.login().open(document)
        self.assertIsNotNone(browser.css('#uploadbox'))
