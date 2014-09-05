from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
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
