from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testing import MockTestCase
from opengever.base.interfaces import IBaseClientID
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex.dossiercover import DossierCoverPDFView
from opengever.latex.dossiercover import IDossierCoverLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing import create_ogds_user
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierCoverRenderArguments(FunctionalTestCase):

    def setUp(self):
        super(TestDossierCoverRenderArguments, self).setUp()

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        proxy.client_title = u'Department of forest & hunt'

        create_ogds_user('hugo.boss')

        repository = create(Builder('repository_root')
                            .having(version='Repository 2013 & 2014'))
        repofolder = create(Builder('repository').within(repository))
        dossier = create(Builder('dossier')
                         .having(title=u'Foo & bar',
                                 responsible='hugo.boss',
                                 start=date(2013, 11, 1),
                                 end=date(2013, 12, 31))
                         .within(repofolder))

        provide_request_layer(dossier.REQUEST, IDossierCoverLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        self.dossiercover = getMultiAdapter(
            (dossier, dossier.REQUEST, layout), ILaTeXView)

    def test_contains_converted_configured_clienttitle(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('Department of forest \\& hunt',
                          arguments.get('clienttitle'))

    def test_contains_repository_version(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'Repository 2013 \\& 2014',
                          arguments.get('repositoryversion'))

    def test_contains_referencenr(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'OG 1 / 1',
                          arguments.get('referencenr'))

    def test_contains_converted_title(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'Foo \\& bar',
                          arguments.get('title'))

    def test_contains_description_of_responsible(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'Boss Hugo (hugo.boss)',
                          arguments.get('responsible'))

    def test_contains_start_date_in_readable_format(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('Nov 01, 2013', arguments.get('start'))

    def test_contains_end_date_in_readable_format(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('Dec 31, 2013', arguments.get('end'))


class TestDossierCoverPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.providing_stub([IDossierMarker])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request), name='dossier_cover_pdf')

        self.assertTrue(isinstance(view, DossierCoverPDFView))

    def test_render_adds_browser_layer(self):
        context = request = self.create_dummy()

        view = self.mocker.patch(DossierCoverPDFView(context, request))

        self.expect(view.allow_alternate_output()).result(False)
        self.expect(view.export())

        self.replay()

        view.render()
        self.assertTrue(IDossierCoverLayer.providedBy(request))
