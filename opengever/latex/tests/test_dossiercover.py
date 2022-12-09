from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from opengever.latex.dossiercover import IDossierCoverLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import create_ogds_user
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter


class TestDossierCoverRenderArguments(FunctionalTestCase):

    def setUp(self):
        super(TestDossierCoverRenderArguments, self).setUp()

        self.user = create_ogds_user('hugo.boss')
        self.repository = create(
            Builder('repository_root')
            .having(version='Repository 2013 & 2014'))
        repofolder = create(Builder('repository').within(self.repository))
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

    @browsing
    def test_dossiercover_view(self, browser):
        dossier = create(Builder('dossier')
                         .within(self.repository)
                         .having(responsible=self.user.userid))

        browser.login().visit(dossier, view='dossier_cover_pdf')

    def test_contains_converted_configured_clienttitle(self):
        get_current_admin_unit().title = u'Department of forest & hunt'
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('Department of forest \\& hunt',
                          arguments.get('clienttitle'))

    def test_empty_client_title(self):
        get_current_admin_unit().title = u''

        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('', arguments.get('clienttitle'))

    def test_contains_repository_version(self):
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'Repository 2013 \\& 2014',
                          arguments.get('repositoryversion'))

    def test_repository_returns_empty_string_and_not_none_if_version_is_not_set(self):
        self.repository.version = None
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals('',
                          arguments.get('repositoryversion'))

    def test_contains_referencenr(self):
        get_current_admin_unit().abbreviation = u'DoFH'
        arguments = self.dossiercover.get_render_arguments()
        self.assertEquals(u'DoFH 1 / 1', arguments.get('referencenr'))

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
