from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDocumentListing(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentListing, self).setUp()

        self.repository = create(Builder('repository'))

        self.dossier = create(Builder('dossier')
                              .within(self.repository)
                              .titled(u'Dossier'))

        self.document_1 = create(Builder('document')
                                 .having(document_date=date(2016, 2, 10),
                                         document_author=u'Peter Meter',
                                         receipt_date=date(2016, 2, 11),
                                         delivery_date=date(2016, 2, 12),
                                         public_trial=u'unchecked')
                                 .within(self.dossier)
                                 .titled(u'Document 1'))

        self.document_2 = create(Builder('document')
                                 .having(document_date=date(2016, 2, 12),
                                         document_author=u'Meter Peter',
                                         receipt_date=date(2016, 2, 13),
                                         delivery_date=date(2016, 2, 14),
                                         public_trial=u'unchecked')
                                 .within(self.dossier)
                                 .titled(u'Document 2'))

    @browsing
    def test_lists_documents(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-documents')

        table = browser.css('.listing').first
        expected = [['',
                     'Sequence Number',
                     'Title',
                     'Document Author',
                     'Document Date',
                     'Receipt Date',
                     'Delivery Date',
                     'Checked out by',
                     'Subdossier',
                     'Public Trial',
                     'Reference Number'],
                    ['',
                     '1',
                     'Document 1',
                     'Peter Meter',     # document_author
                     '10.02.2016',      # document_date
                     '11.02.2016',      # receipt_date
                     '12.02.2016',      # delivery_date
                     '',
                     '',
                     'unchecked',       # public_trial
                     'Client1 1 / 1 / 1'],
                    ['',
                     '2',
                     'Document 2',
                     'Meter Peter',
                     '12.02.2016',
                     '13.02.2016',
                     '14.02.2016',
                     '',
                     '',
                     'unchecked',
                     'Client1 1 / 1 / 2']]

        self.assertEquals(expected, table.lists())
