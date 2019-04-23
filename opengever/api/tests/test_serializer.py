from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
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
        browser.open(
            self.leaf_repofolder, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1')

    @browsing
    def test_repofolder_serialization_contains_is_leafnode(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.leaf_repofolder, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'is_leafnode'), True)

    @browsing
    def test_repofolder_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.leaf_repofolder, headers={'Accept': 'application/json'})
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
        browser.open(self.dossier, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1')

    @browsing
    def test_dossier_serialization_contains_email(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'email'), u'1014013300@example.org')

    @browsing
    def test_dossier_serialization_contains_responsible_fullname(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'responsible_fullname'), u'Ziegler Robert')

    @browsing
    def test_dossier_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1')


class TestDocumentSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_document_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 14')

    @browsing
    def test_document_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'bumblebee_checksum'), DOCX_CHECKSUM)

    @browsing
    def test_document_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.document.getId()))

    @browsing
    def test_mail_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers={'Accept': 'application/json'})
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 29', browser.json.get(u'reference_number'))

    @browsing
    def test_mail_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)

        checksum = IBumblebeeDocument(self.mail_eml).get_checksum()
        self.assertEqual(browser.json.get(u'bumblebee_checksum'), checksum)

    @browsing
    def test_mail_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'relative_path'),
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.mail_eml.getId()))
