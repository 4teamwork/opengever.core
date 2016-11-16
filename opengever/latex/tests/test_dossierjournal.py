from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from ftw.testing import MockTestCase
from opengever.latex import dossierjournal
from opengever.latex.dossierjournal import IDossierJournalLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierJournalPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request), name='pdf-dossier-journal')
        self.assertTrue(isinstance(view, dossierjournal.DossierJournalPDFView))

    def test_render_adds_browser_layer(self):
        context = request = self.create_dummy()

        view = self.mocker.patch(
            dossierjournal.DossierJournalPDFView(context, request))

        self.expect(view.allow_alternate_output()).result(False)
        self.expect(view.export())

        self.replay()

        view.render()
        self.assertTrue(
            dossierjournal.IDossierJournalLayer.providedBy(request))


class TestDossierListingLaTeXView(FunctionalTestCase):

    @browsing
    def test_journal_listing(self, browser):
        repo = create(Builder('repository'))

        with freeze(datetime(2016, 4, 12, 10, 35)):
            browser.login().open(repo)

            factoriesmenu.add('Business Case Dossier')
            browser.fill({'Title': u'Dossier A'})
            browser.find('Save').click()
            dossier = browser.context

            factoriesmenu.add('Document')
            browser.fill({'Title': u'Document A'})
            browser.find('Save').click()

            expected_date = DateTime()

        provide_request_layer(dossier.REQUEST, IDossierJournalLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        dossierjournal = getMultiAdapter((dossier, dossier.REQUEST, layout),
                                         ILaTeXView)

        expected = [{'action': {'visible': True,
                                'type': 'Dossier added',
                                'title': u'label_dossier_added'},
                     'comments': '',
                     'actor': 'test_user_1_',
                     'time': expected_date},

                    {'action': {'visible': True,
                                'type': 'Document added',
                                'title': u'label_document_added'},
                     'comments': '',
                     'actor': 'test_user_1_',
                     'time': expected_date},

                    {'action': {'visible': False,
                                'type': 'Dossier modified',
                                'title': u'label_dossier_modified'},
                     'comments': '',
                     'actor': 'test_user_1_',
                     'time': expected_date}]

        self.assertEquals(expected, dossierjournal.get_journal_data())
