from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex import dossierdetails
from opengever.latex.testing import LATEX_ZCML_LAYER
from zope.component import adaptedBy
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierDetailsPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.providing_stub([IDossierMarker])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request),
                               name='pdf-dossier-details')

        self.assertTrue(isinstance(
                view, dossierdetails.DossierDetailsPDFView))

    def test_render_adds_browser_layer(self):
        context = request = self.create_dummy()

        view = self.mocker.patch(
            dossierdetails.DossierDetailsPDFView(context, request))

        self.expect(view.allow_alternate_output()).result(False)
        self.expect(view.export())

        self.replay()

        view.render()
        self.assertTrue(dossierdetails.IDossierDetailsLayer.providedBy(
                request))
