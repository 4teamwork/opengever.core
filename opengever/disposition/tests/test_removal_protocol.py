from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from lxml.cssselect import CSSSelector
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.disposition.browser.removal_protocol import IRemovalProtocolLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.listing import ILaTexListing
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter
import lxml


class TestDestroyedDossierListing(FunctionalTestCase):

    def setUp(self):
        super(TestDestroyedDossierListing, self).setUp()
        dossier_a = create(Builder('dossier')
                           .as_expired()
                           .titled(u'Dossier A'))
        dossier_b = create(Builder('dossier')
                           .as_expired()
                           .having(archival_value=ARCHIVAL_VALUE_UNWORTHY)
                           .titled(u'Dossier B'))

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

        self.assertEquals(
            ['Client1 / 1', 'Dossier A', 'Yes'],
            [value.text_content().strip() for value in
             rows[0].xpath(CSSSelector('td').path)])

        self.assertEquals(
            ['Client1 / 2', 'Dossier B', 'No'],
            [value.text_content().strip() for value in
             rows[1].xpath(CSSSelector('td').path)])


class TestRemovalProtocolLaTeXView(FunctionalTestCase):

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
