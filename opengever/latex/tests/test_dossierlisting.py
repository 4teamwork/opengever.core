from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.latex import dossierlisting
from opengever.latex.testing import LATEX_ZCML_LAYER
from zope.component import adaptedBy
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierListingPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request),
                               name='pdf-dossier-listing')

        self.assertTrue(isinstance(
                view, dossierlisting.DossierListingPDFView))

    def test_render_adds_browser_layer(self):
        context = request = self.create_dummy()

        view = self.mocker.patch(
            dossierlisting.DossierListingPDFView(context, request))

        self.expect(view.allow_alternate_output()).result(False)
        self.expect(view.export())

        self.replay()

        view.render()
        self.assertTrue(dossierlisting.IDossierListingLayer.providedBy(
                request))


class TestDossierListingLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_component_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([dossierlisting.IDossierListingLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)

        self.assertEqual(type(view), dossierlisting.DossierListingLaTeXView)

    def test_implements_interface(self):
        self.assertTrue(ILaTeXView.implementedBy(
                dossierlisting.DossierListingLaTeXView))

        verifyClass(ILaTeXView, dossierlisting.DossierListingLaTeXView)

    def test_adapts_layer(self):
        context_iface, request_iface, layout_iface = adaptedBy(
            dossierlisting.DossierListingLaTeXView)

        self.assertEqual(request_iface, dossierlisting.IDossierListingLayer)

    def test_get_repository_title(self):
        baseurl = 'http://127.0.0.1:8080/mandant2/ordnungssystem'

        main_breadcrumb_titles = [
            {'absolute_url': baseurl,
             'Title': 'Ordnungssystem'},

            {'absolute_url': '%s/fuehrung' % baseurl,
             'Title': u'1. Fuehrung'},

            {'absolute_url': '%s/fuehrung/berichtwesen' % baseurl,
             'Title': u'1.2. Berichtwesen'},

            {'absolute_url': '%s/fuehrung/berichtwesen/dossier-6' % baseurl,
             'Title': u'main dossier'}]

        main_dossier = self.create_dummy(
            reference='OG 1.2 / 2',
            breadcrumb_titles=main_breadcrumb_titles)

        sub_breadcrumb_titles = main_breadcrumb_titles + [
            {'absolute_url': baseurl + \
                 '/fuehrung/berichtwesen/dossier-6/dossier-14',
             'Title': u'sub dossier'}]

        sub_dossier = self.create_dummy(
            reference='OG 1.2 / 2.1',
            breadcrumb_titles=sub_breadcrumb_titles)

        wrong_dossier = self.create_dummy(
            reference='OG 1',
            breadcrumb_titles=sub_breadcrumb_titles)

        context = request = layout = object()
        self.replay()
        view = dossierlisting.DossierListingLaTeXView(
            context, request, layout)

        self.assertEqual(view.get_repository_title(main_dossier),
                         '1.2. Berichtwesen')

        self.assertEqual(view.get_repository_title(sub_dossier),
                         '1.2. Berichtwesen')

        self.assertEqual(view.get_repository_title(wrong_dossier),
                         '')

    def test_convert_list_to_row(self):
        context = self.create_dummy()
        request = self.providing_stub([dossierlisting.IDossierListingLayer])
        builder = self.providing_stub([IBuilder])
        self.replay()

        layout = getMultiAdapter((context, request, builder), ILaTeXLayout)

        view = dossierlisting.DossierListingLaTeXView(
            context, request, layout)

        input = ['f\xc3\xbc', None, u'b\xe4r', 15]
        output = 'f\xc3\xbc &  & b\xc3\xa4r & 15'

        self.assertEqual(view.convert_list_to_row(input), output)
