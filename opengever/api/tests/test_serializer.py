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
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 12')

    @browsing
    def test_mail_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 29')
