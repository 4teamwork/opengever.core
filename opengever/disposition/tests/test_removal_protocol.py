from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from opengever.disposition.browser.removal_protocol import IRemovalProtocolLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestRemovalProtocolLaTeXView(IntegrationTestCase):

    def get_view(self, disposition):
        provide_request_layer(disposition.REQUEST, IRemovalProtocolLayer)
        layout = DefaultLayout(disposition, disposition.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (disposition, disposition.REQUEST, layout), ILaTeXView)

    def test_disposition_metadata(self):
        self.login(self.records_manager)
        self.disposition.transfer_number = "RSX 382"

        self.assertEquals(
            u'\\bf Title & Angebot 31.8.2016 \\\\%%\n\\bf '
            'Transfer number & RSX 382 \\\\%%',
            self.get_view(self.disposition).get_disposition_metadata())

    @browsing
    def test_pdf_title_is_removal_protocol_for_disposition_title(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='removal_protocol')

        self.assertEquals(
            'attachment; filename="Removal protocol for {}.pdf"'.format(self.disposition.title),
            browser.headers.get('content-disposition'))
