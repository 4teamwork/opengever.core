from DateTime import DateTime
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testing import MockTestCase
from opengever.latex import dossierjournal
from opengever.latex.dossierjournal import IDossierJournalLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierJournalPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request), name='pdf-dossier-journal')
        self.assertTrue(isinstance(view, dossierjournal.DossierJournalPDFView))


class TestJournalListingLaTeXView(IntegrationTestCase):

    features = ('journal-pdf',)

    def setUp(self):
        super(TestJournalListingLaTeXView, self).setUp()
        self.request = getRequest()
        provide_request_layer(self.request, IDossierJournalLayer)

    def test_journal_label(self):
        self.login(self.regular_user)
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        dossier_journal = getMultiAdapter(
            (self.dossier, self.request, layout), ILaTeXView)
        self.assertEqual(
            'Journal of dossier "`Vertr\xc3\xa4ge mit der kantonalen'
            ' Finanzverwaltung (Client1 1.1 / 1)"\'',
            dossier_journal.get_render_arguments().get('label'),
        )

    def test_journal_listing(self):
        self.login(self.regular_user)
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        dossier_journal = getMultiAdapter(
            (self.dossier, self.request, layout), ILaTeXView)
        expected_journal = [
            {
                'action': {
                    'visible': True,
                    'type': 'Dossier added',
                    'title': u'label_dossier_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 16:01:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 16:07:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 16:29:42 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 17:01:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 17:03:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'franzi.muller',
                'time': DateTime('2016/08/31 17:17:35 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task added',
                    'title': u'label_task_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:01:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task modified',
                    'title': u'label_task_modified',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:03:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task modified',
                    'title': u'label_task_modified',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:05:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task added',
                    'title': u'label_task_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:07:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task modified',
                    'title': u'label_task_modified',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:09:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task modified',
                    'title': u'label_task_modified',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:11:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task modified',
                    'title': u'label_task_modified',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:13:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task added',
                    'title': u'label_task_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:23:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task added',
                    'title': u'label_task_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:25:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Task added',
                    'title': u'label_task_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 18:27:33 GMT+2'),
            },
            {
                'action': {
                    'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added',
                },
                'comments': '',
                'actor': 'robert.ziegler',
                'time': DateTime('2016/08/31 20:05:33 GMT+2'),
            },
        ]
        self.assertEqual(expected_journal, dossier_journal.get_journal_data())

    def test_handle_special_white_space_characters(self):
        self.login(self.regular_user)
        self.dossier.title = u' '.join((
            u'vertical\x0btab', self.dossier.title))
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        dossier_journal = getMultiAdapter(
            (self.dossier, self.request, layout), ILaTeXView)
        self.assertEqual(
            'Journal of dossier "`vertical tab Vertr\xc3\xa4ge mit der'
            ' kantonalen Finanzverwaltung (Client1 1.1 / 1)"\'',
            dossier_journal.get_render_arguments().get('label'),
        )

    def test_handle_complex_urls(self):
        self.login(self.regular_user)
        self.dossier.title = (
            u'https://example.com/some.php?get1=1234'
            '&weird_get_%5Bbracketed%5D=5678&somemore=blah'
        )  # Do not add commas above, this is a string!
        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        dossier_journal = getMultiAdapter(
            (self.dossier, self.request, layout), ILaTeXView)
        self.assertEqual(
            'Journal of dossier "`https://example.com""/some.php?get1=1234'
            '""\\&weird\\_get\\_\\%5Bbracketed\\%5D=5678'
            '""\\&somemore=blah (Client1 1.1 / 1)"\'',
            dossier_journal.get_render_arguments().get('label'),
        )
