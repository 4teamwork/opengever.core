from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from ftw.testing import freeze
from lxml.cssselect import CSSSelector
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.disposition.browser.removal_protocol import IRemovalProtocolLayer
from opengever.disposition.interfaces import IHistoryStorage
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.listing import ILaTexListing
from opengever.latex.tests.test_listing import BaseLatexListingTest
from opengever.testing import FunctionalTestCase
from plone import api
from zope.component import getMultiAdapter
import lxml


class TestDestroyedDossierListing(BaseLatexListingTest):

    def setUp(self):
        super(TestDestroyedDossierListing, self).setUp()
        dossier_a = create(Builder('dossier')
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_WORTHY)
                           .titled(u'Dossier A'))
        dossier_b = create(Builder('dossier')
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                           .titled(u'Dossier B'))

        self.grant('Records Manager')

        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[dossier_a, dossier_b])
                                  .in_state('disposition-state-closed'))
        self.disposition.set_destroyed_dossiers([dossier_a, dossier_b])

        self.listing = getMultiAdapter(
            (self.disposition, self.disposition.REQUEST, self),
            ILaTexListing, name='destroyed_dossiers')

    def test_listing(self):
        self.listing.items = self.disposition.get_dossier_representations()

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['Client1 / 1', 'Dossier A', 'Yes'], rows[0])
        self.assert_row_values(
            ['Client1 / 2', 'Dossier B', 'No'], rows[1])


class TestDispositionHistoryListing(BaseLatexListingTest):

    def setUp(self):
        super(TestDispositionHistoryListing, self).setUp()
        self.dossier = create(Builder('dossier')
                              .as_expired()
                              .having(archival_value=ARCHIVAL_VALUE_WORTHY))

    def test_listing(self):
        self.grant('Records Manager', 'Archivist')
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier]))

        with freeze(datetime(2014, 11, 6, 12, 33)):
            api.content.transition(disposition,
                                   'disposition-transition-appraise')
            api.content.transition(disposition,
                                   'disposition-transition-dispose')

        with freeze(datetime(2014, 11, 16, 8, 12)):
            api.content.transition(disposition,
                                   'disposition-transition-archive')

        self.listing = getMultiAdapter(
            (disposition, disposition.REQUEST, self),
            ILaTexListing, name='disposition_history')
        self.listing.items = disposition.get_history()

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['Nov 16, 2014 08:12 AM',
             'Test User (test_user_1_)',
             'disposition-transition-archive'], rows[0])

        self.assert_row_values(
            ['Nov 06, 2014 12:33 PM',
             'Test User (test_user_1_)',
             'disposition-transition-dispose'], rows[1])

        self.assert_row_values(
            ['Nov 06, 2014 12:33 PM',
             'Test User (test_user_1_)',
             'disposition-transition-appraise'], rows[2])

    def test_transition_label_for_added_and_edited_entries_is_translated_correctly(self):
        disposition = create(Builder('disposition'))

        storage = IHistoryStorage(disposition)
        storage.add('added', api.user.get_current().getId(), [])
        storage.add('edited', api.user.get_current().getId(), [])

        self.listing = getMultiAdapter(
            (disposition, disposition.REQUEST, self),
            ILaTexListing, name='disposition_history')
        self.listing.items = disposition.get_history()

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['Disposition edited'], rows[0][2])
        self.assert_row_values(
            ['Disposition added'], rows[1][2])


class TestRemovalProtocolLaTeXView(FunctionalTestCase):

    def setUp(self):
        super(TestRemovalProtocolLaTeXView, self).setUp()

        self.grant('Records Manager')

    def get_view(self, disposition):
        provide_request_layer(disposition.REQUEST, IRemovalProtocolLayer)
        layout = DefaultLayout(disposition, disposition.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (disposition, disposition.REQUEST, layout), ILaTeXView)

    def test_disposition_metadata(self):
        disposition = create(Builder('disposition')
                             .having(title=u'Angebot FD 43929',
                                     transfer_number='RSX 382'))

        self.assertEquals(
            u'\\bf Title & Angebot FD 43929 \\\\%%\n\\bf '
            'Transfer number & RSX 382 \\\\%%',
            self.get_view(disposition).get_disposition_metadata())

    @browsing
    def test_pdf_title_is_removal_protocol_for_disposition_title(self, browser):
        disposition = create(Builder('disposition')
                             .having(title=u'Angebot FD 43929',
                                     transfer_number='RSX 382'))

        browser.login().open(disposition, view='removal_protocol')

        self.assertEquals(
            'attachment; filename="Removal protocol for Angebot FD 43929.pdf"',
            browser.headers.get('content-disposition'))
