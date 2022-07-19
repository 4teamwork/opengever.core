from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.latex import dossierdetails
from opengever.latex.dossierdetails import IDossierDetailsLayer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import json
import requests_mock


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

        view()
        self.assertTrue(dossierdetails.IDossierDetailsLayer.providedBy(
                        request))


class TestDossierDetailsBase(IntegrationTestCase):

    def setUp(self):
        super(TestDossierDetailsBase, self).setUp()
        with self.login(self.regular_user):
            # responsibles are not set in the fixture
            for obj in (self.subdossier, self.subsubdossier, self.subdossier2):
                IDossier(obj).responsible = self.regular_user.id
                obj.reindexObject(idxs=["responsible"])

    def get_dossierdetails_view(self, dossier):
        provide_request_layer(dossier.REQUEST, IDossierDetailsLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (dossier, dossier.REQUEST, layout), ILaTeXView)


class TestDossierDetails(TestDossierDetailsBase):

    @browsing
    def test_dossierdetails_view(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.dossier, view='pdf-dossier-details')

    def test_responsible_contains_admin_unit_and_userid(self):
        self.login(self.regular_user)
        dossierdetails = self.get_dossierdetails_view(self.subdossier2)
        self.assertEquals(
            'Hauptmandant / B\xc3\xa4rfuss K\xc3\xa4thi (kathi.barfuss)',
            dossierdetails.get_responsible().encode('utf-8'))

    @browsing
    def test_custom_fields_on_dossier_details(self, browser):
        self.login(self.regular_user, browser)
        PropertySheetSchemaStorage().clear()
        choices = ["one", u"zw\xf6i", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDossier.default")
            .with_field("choice", u"choose", u"Choose", u"", False, values=choices)
            .with_field("multiple_choice", u"choosemulti",
                        u"Choose Multi", u"", False, values=choices)
            .with_field("textline", u"textline", u"A line of text", u"", False)
            .with_field("date", u"birthday", u"Birthday", u"", False)
            .with_field("int", u"num", u"Number", u"", False)
            .with_field("text", u"text", u"Some lines of text", u"", False)
            .with_field("bool", u"yesorno", u"Yes or no", u"", False)
        )

        property_data = {
            "IDossier.default": {
                "choose": u"zw\xf6i".encode("unicode_escape"),
                "choosemulti": ["one", "three"],
                "textline": u"bl\xe4",
                "birthday": "2022-01-30",
                "num": 12,
                "text": u"Irgend \xe4 Texscht",
                "yesorno": True,
            },
        }
        data = {
            "@type": "opengever.dossier.businesscasedossier",
            "title": "New Dossier",
            "responsible": self.regular_user.getId(),
            "custom_properties": property_data,
        }

        with self.observe_children(self.leaf_repofolder) as children:
            browser.login().open(self.leaf_repofolder, method="POST",
                                 data=json.dumps(data), headers=self.api_headers)

        dossier = children["added"].pop()
        dossierdetails = self.get_dossierdetails_view(dossier)
        self.assertEqual('\\bf Choose & zw\xc3\xb6i \\\\%%\n'
                         '\\bf Choose Multi & three, one \\\\%%\n'
                         '\\bf A line of text & bl\xc3\xa4 \\\\%%\n'
                         '\\bf Birthday & 30.01.2022 \\\\%%\n'
                         '\\bf Number & 12 \\\\%%\n'
                         '\\bf Some lines of text & Irgend \xc3\xa4 Texscht \\\\%%\n'
                         '\\bf Yes or no & Yes \\\\%%', dossierdetails.get_custom_fields_data())

    def test_repository_path_is_a_reverted_path_seperated_with_slahes(self):
        self.login(self.regular_user)
        dossierdetails = self.get_dossierdetails_view(self.dossier)
        self.assertEquals(
            '1.1. Vertr\xc3\xa4ge und Vereinbarungen / 1. F\xc3\xbchrung',
            dossierdetails.get_repository_path())

    def test_repository_path_do_not_escape_special_latex_characters(self):
        """The escaping is done by the `get_dossier_metadata` method
        and shouldn't be done twice."""
        self.login(self.regular_user)
        self.leaf_repofolder.title_en = u'Foo & Bar'

        dossierdetails = self.get_dossierdetails_view(self.dossier)

        self.assertEquals(
            '1.1. Foo & Bar / 1. F\xc3\xbchrung',
            dossierdetails.get_repository_path())

    def test_handles_plone_participations(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.regular_user.getId(),
                                  ['regard', 'participation', 'final-drawing'])
        handler.add_participation(self.dossier_responsible.getId(), ['regard'])

        dossierdetails = self.get_dossierdetails_view(self.dossier)
        dossierdetails.get_participants()
        self.assertEqual(
            ['{ ',
             '\\vspace{-\\baselineskip}\\begin{itemize} ',
             '\\item Ziegler Robert (robert.ziegler), Responsible ',
             '\\item B\xc3\xa4rfuss K\xc3\xa4thi (kathi.barfuss), For your information, Participation, Final signature ',
             '\\item Ziegler Robert (robert.ziegler), For your information ',
             '\\vspace{-\\baselineskip}\\end{itemize} ',
             '}'],
            dossierdetails.get_participants().split("\n")
        )

    def test_handles_sql_participations(self):
        self.activate_feature('contact')

        self.login(self.regular_user)

        dossierdetails = self.get_dossierdetails_view(self.dossier)
        dossierdetails.get_participants()
        self.assertEqual(
            ['{ ',
             '\\vspace{-\\baselineskip}\\begin{itemize} ',
             '\\item Ziegler Robert (robert.ziegler), Responsible ',
             '\\item Meier AG, Final signature ',
             '\\item B\xc3\xbchler Josef, Final signature, Participation ',
             '\\vspace{-\\baselineskip}\\end{itemize} ',
             '}'],
            dossierdetails.get_participants().split("\n")
        )


@requests_mock.Mocker()
class TestDossierDetailsWithKuB(KuBIntegrationTestCase, TestDossierDetailsBase):

    def test_handles_kub_participations(self, mocker):
        self.activate_feature('contact')

        self.login(self.regular_user)

        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, 'person:9af7d7cc-b948-423f-979f-587158c6bc65')
        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            'person:9af7d7cc-b948-423f-979f-587158c6bc65', ['regard'])

        dossierdetails = self.get_dossierdetails_view(self.dossier)
        dossierdetails.get_participants()
        self.assertEqual(
            ['{ ',
             '\\vspace{-\\baselineskip}\\begin{itemize} ',
             '\\item Ziegler Robert (robert.ziegler), Responsible ',
             '\\item Dupont Jean, For your information ',
             '\\vspace{-\\baselineskip}\\end{itemize} ',
             '}'],
            dossierdetails.get_participants().split("\n")
        )
