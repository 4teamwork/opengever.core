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
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
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

        client1 = create_client()
        create_ogds_user(TEST_USER_ID, assigned_client=[client1],
                         firstname='t\xc3\xa4st'.decode('utf-8'),
                         lastname=u'User')
        set_current_client_id(self.portal)

    def dossierdetails_view(self, dossier):
        provide_request_layer(dossier.REQUEST, IDossierDetailsLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (dossier, dossier.REQUEST, layout), ILaTeXView)

    def test_responsible_contains_client_and_userid_splited_with_a_slash(self):
        dossier = create(Builder('dossier')
                 .having(responsible=TEST_USER_ID))

        dossierdetails = self.dossierdetails_view(dossier)
        self.assertEquals(
            'Client1 / User t\xc3\xa4st (test_user_1_)'.decode('utf-8'),
            dossierdetails.get_responsible())
