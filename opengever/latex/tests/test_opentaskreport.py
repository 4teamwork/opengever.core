from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex import opentaskreport
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.opentaskreport import IOpenTaskReportLayer
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.ogds.base.interfaces import IContactInformation
from opengever.testing import FunctionalTestCase
from zope.component import adaptedBy
from zope.component import getMultiAdapter
from zope.component import getUtility
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


class TestOpenTaskReport(FunctionalTestCase):

    def setUp(self):
        super(TestOpenTaskReport, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())
        self.task = create(Builder("task").having(task_type='comment',
                                                  issuer='peter.peter',
                                                  responsible='hans.meier'))

        self.hans = create(Builder('ogds_user')
                           .having(userid='hans.meier',
                                   firstname='Hans',
                                   lastname='Meier'))
        self.peter = create(Builder('ogds_user')
                            .having(userid='peter.peter',
                                    firstname='Peter',
                                    lastname='Peter'))

        provide_request_layer(self.task.REQUEST, IOpenTaskReportLayer)
        layout = DefaultLayout(self.task, self.task.REQUEST, PDFBuilder())
        self.opentaskreport = getMultiAdapter(
            (self.task, self.task.REQUEST, layout), ILaTeXView)
        # hack, this is set when calling `get_render_arguments`, XXX remove
        self.opentaskreport.info = getUtility(IContactInformation)

    def test_actor_labels_are_visible_in_task_listing(self):
        row = self.opentaskreport.get_data_for_item(self.task.get_sql_object())
        self.assertIn(self.peter.label(with_principal=False), row)
        self.assertIn(self.hans.label(with_principal=False), row)

    @browsing
    def test_smoke_open_task_report_view(self, browser):
        browser.login().open(view='pdf-open-task-report')
