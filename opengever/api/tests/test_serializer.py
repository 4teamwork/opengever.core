from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from opengever.testing import IntegrationTestCase
from plone import api


class TestRepositoryFolderSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestRepositoryFolderSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_repofolder_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1')

    @browsing
    def test_repofolder_serialization_contains_is_leafnode(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'is_leafnode'), True)

    @browsing
    def test_repofolder_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen')


class TestDossierSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDossierSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_dossier_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1')

    @browsing
    def test_dossier_serialization_contains_email(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'email'), u'1014013300@example.org')

    @browsing
    def test_dossier_serialization_contains_responsible_fullname(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'responsible_fullname'), u'Ziegler Robert')

    @browsing
    def test_dossier_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1')

    @browsing
    def test_dossier_serialization_contains_is_subdossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'is_subdossier'),
            False)

        browser.open(self.subdossier, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'is_subdossier'),
            True)


class TestDocumentSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_document_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 14')

    @browsing
    def test_document_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'bumblebee_checksum'), DOCX_CHECKSUM)

    @browsing
    def test_document_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.document.getId()))

    @browsing
    def test_mail_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 29', browser.json.get(u'reference_number'))

    @browsing
    def test_mail_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)

        checksum = IBumblebeeDocument(self.mail_eml).get_checksum()
        self.assertEqual(browser.json.get(u'bumblebee_checksum'), checksum)

    @browsing
    def test_mail_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.mail_eml.getId()))


class TestInboxSerializer(IntegrationTestCase):

    @browsing
    def test_inbox_serialization_contains_email(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'email'), u'1011013300@example.org')

    @browsing
    def test_inbox_serialization_contains_inbox_id(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'inbox_id'), u'inbox:fa')

    @browsing
    def test_inbox_id_defaults_to_current_orgunit(self, browser):
        self.login(self.manager, browser)
        IResponsibleOrgUnit(self.inbox).responsible_org_unit = None

        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'inbox_id'), u'inbox:fa')

        # change orgunit
        browser.open(self.repository_root)
        browser.css('.orgunitMenuContent a')[0].click()

        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'inbox_id'), u'inbox:rk')
