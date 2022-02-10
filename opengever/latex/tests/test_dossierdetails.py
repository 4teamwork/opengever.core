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
from ftw.testbrowser import browsing
import json


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


class TestDossierDetails(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestDossierDetails, self).setUp()
        self.user = create(Builder('ogds_user')
                           .having(firstname='t\xc3\xa4st'.decode('utf-8'),
                                   lastname=u'User'))
        self.admin_unit = create(Builder('admin_unit')
                                 .as_current_admin_unit()
                                 .having(title=u'Regierungsrat'))
        self.org_unit = create(Builder('org_unit')
                               .having(title=u'Regierungsrat',
                                       admin_unit=self.admin_unit)
                               .with_default_groups()
                               .assign_users([self.user]))

        select_current_org_unit(self.org_unit.id())

    @browsing
    def test_dossierdetails_view(self, browser):
        repositoryroot = create(Builder('repository_root')
                                .titled(u'Repository'))
        repository_1 = create(Builder('repository')
                              .titled(u'Repository Folder')
                              .within(repositoryroot))
        repository_1_1 = create(Builder('repository')
                                .titled(u'Sub Repository Folder')
                                .within(repository_1))
        dossier = create(Builder('dossier')
                         .within(repository_1_1)
                         .having(responsible=self.user.userid))
        create(Builder('task')
               .within(dossier)
               .having(responsible=self.user.userid,
                       responsible_client=self.org_unit.id()))

        browser.login().visit(dossier, view='pdf-dossier-details')

    def get_dossierdetails_view(self, dossier):
        provide_request_layer(dossier.REQUEST, IDossierDetailsLayer)
        layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
        return getMultiAdapter(
            (dossier, dossier.REQUEST, layout), ILaTeXView)

    def test_responsible_contains_admin_unit_and_userid(self):
        dossier = create(Builder('dossier')
                         .having(responsible=TEST_USER_ID))

        dossierdetails = self.get_dossierdetails_view(dossier)
        self.assertEquals(
            'Regierungsrat / User t\xc3\xa4st (test_user_1_)',
            dossierdetails.get_responsible().encode('utf-8'))

    @browsing
    def test_custom_fields_on_dossier_details(self, browser):
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
        repository = create(Builder('repository')
                            .titled(u'Repository Folder'))
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
            "responsible": TEST_USER_ID,
            "custom_properties": property_data,
        }

        with self.observe_children(repository) as children:
            browser.login().open(repository, method="POST", data=json.dumps(data),
                                 headers={'Accept': 'application/json',
                                          'Content-Type': 'application/json'})

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
