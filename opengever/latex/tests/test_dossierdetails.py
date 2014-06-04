from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.latex import dossierdetails
from opengever.latex.dossierdetails import IDossierDetailsLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.testing import FunctionalTestCase
from opengever.testing import select_current_org_unit
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
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


class TestDossierDetailsDossierMetadata(FunctionalTestCase):

    def setUp(self):
        super(TestDossierDetailsDossierMetadata, self).setUp()
        self.user = create(Builder('ogds_user')
                           .having(firstname='t\xc3\xa4st'.decode('utf-8'),
                                   lastname=u'User'))
        self.org_unit = create(Builder('org_unit')
                               .having(title=u'Regierungsrat')
                               .with_default_groups()
                               .assign_users([self.user]))
        self.admin_unit = create(Builder('admin_unit')
                                 .as_current_admin_unit()
                                 .wrapping_org_unit(self.org_unit))

        select_current_org_unit(self.org_unit.id())

    def get_dossierdetails_view(self, dossier):
        provide_request_layer(dossier.REQUEST, IDossierDetailsLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (dossier, dossier.REQUEST, layout), ILaTeXView)

    def test_responsible_contains_client_and_userid_separated_by_a_slash(self):
        dossier = create(Builder('dossier')
                         .having(responsible=TEST_USER_ID))

        dossierdetails = self.get_dossierdetails_view(dossier)
        self.assertEquals(
            'Regierungsrat / User t\xc3\xa4st (test_user_1_)',
            dossierdetails.get_responsible().encode('utf-8'))

    def test_repository_path_is_a_reverted_path_seperated_with_slahes(self):
        repositoryroot = create(Builder('repository_root')
                                .titled(u'Repository'))
        repository_1 = create(Builder('repository')
                              .titled(u'Repository Folder')
                              .within(repositoryroot))
        repository_1_1 = create(Builder('repository')
                                .titled(u'Sub Repository Folder')
                                .within(repository_1))
        dossier = create(Builder('dossier').within(repository_1_1))

        dossierdetails = self.get_dossierdetails_view(dossier)

        self.assertEquals(
            u'1.1. Sub Repository Folder / 1. Repository Folder',
            dossierdetails.get_repository_path())

    def test_repository_path_do_not_escape_special_latex_characters(self):
        """The escaping is done by the `get_dossier_metadata` method
        and shouldn't be done twice."""

        repofolder = create(Builder('repository')
                              .titled(u'Foo & Bar'))

        dossier = create(Builder('dossier').within(repofolder))
        dossierdetails = self.get_dossierdetails_view(dossier)

        self.assertEquals(
            '1. Foo & Bar',
            dossierdetails.get_repository_path())
