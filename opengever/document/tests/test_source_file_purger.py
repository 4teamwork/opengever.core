from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.document import IDocumentSchema
from opengever.testing import FunctionalTestCase


class TestSourceFilePurgerView(FunctionalTestCase):

    def setUp(self):
        super(TestSourceFilePurgerView, self).setUp()
        self.grant('Records Manager', 'Editor', 'Contributor')

        dossier_a = create(Builder('dossier')
                           .titled(u'Dossier A')
                           .having(end=date(2013, 2, 1)))
        self.document_a = create(Builder('document')
               .titled(u'Document A')
               .attach_archival_file_containing('DATA')
               .within(dossier_a))
        dossier_b = create(Builder('dossier')
                           .titled(u'Dossier B')
                           .having(end=date(2013, 5, 12)))
        self.document_b = create(Builder('document')
               .titled(u'Document B')
               .attach_archival_file_containing('DATA')
               .within(dossier_b))
        self.document_c = create(Builder('document')
               .titled(u'Document C')
               .attach_archival_file_containing('DATA')
               .within(dossier_b))

    @browsing
    def test_lists_all_expired_dossiers(self, browser):
        browser.login().open(self.portal, view='source_file_purger')
        self.assertEquals(
            ['Dossier A', 'Dossier B'],
            browser.css('ul.dossiers li').text)

    @browsing
    def test_lists_all_documents_to_remove(self, browser):
        browser.login().open(self.portal, view='source_file_purger')
        self.assertEquals(
            ['Document A', 'Document B', 'Document C'],
            browser.css('ul.documents li').text)

    @browsing
    def test_purge_all_documents(self, browser):
        browser.login().open(self.portal, view='source_file_purger')
        browser.click_on('Purge all source files')

        self.assertIsNone(IDocumentSchema(self.document_a).file)
        self.assertIsNone(IDocumentSchema(self.document_b).file)
        self.assertIsNone(IDocumentSchema(self.document_c).file)

        self.assertEquals(self.portal.absolute_url(), browser.url)
        self.assertEquals(['The source files has been purged successfully.'],
                          info_messages())
