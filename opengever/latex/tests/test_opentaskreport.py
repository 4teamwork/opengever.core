from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex import opentaskreport
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base import utils
from zope.component import adaptedBy
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestOpenTaskReportPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.providing_stub([IDossierMarker])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request),
                               name='pdf-open-task-report')

        self.assertTrue(isinstance(
                view, opentaskreport.OpenTaskReportPDFView))

    def test_render_adds_browser_layer(self):
        context = request = self.create_dummy()

        view = self.mocker.patch(
            opentaskreport.OpenTaskReportPDFView(context, request))

        self.expect(view.allow_alternate_output()).result(False)
        self.expect(view.export())

        self.replay()

        view.render()
        self.assertTrue(opentaskreport.IOpenTaskReportLayer.providedBy(
                request))


class TestOpenTaskReportLaTeXView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def setUp(self):
        self.ori_get_client_id = utils.get_client_id
        get_client_id = self.mocker.replace(
            'opengever.ogds.base.utils.get_client_id', count=False)
        self.expect(get_client_id()).result('client1')

    def tearDown(self):
        utils.get_client_id = self.ori_get_client_id

    def test_component_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([opentaskreport.IOpenTaskReportLayer])
        layout = self.providing_stub([ILaTeXLayout])

        self.replay()

        view = getMultiAdapter((context, request, layout), ILaTeXView)

        self.assertEqual(type(view), opentaskreport.OpenTaskReportLaTeXView)

    def test_implements_interface(self):
        self.replay()
        self.assertTrue(ILaTeXView.implementedBy(
                opentaskreport.OpenTaskReportLaTeXView))

        verifyClass(ILaTeXView, opentaskreport.OpenTaskReportLaTeXView)

    def test_adapts_layer(self):
        self.replay()
        context_iface, request_iface, layout_iface = adaptedBy(
            opentaskreport.OpenTaskReportLaTeXView)

        self.assertEqual(request_iface, opentaskreport.IOpenTaskReportLayer)
