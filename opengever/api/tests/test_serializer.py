from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestDossierSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDossierSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_dossier_serialization_contains_reference_number(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.dossier, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1')


class TestDocumentSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_document_serialization_contains_reference_number(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 5')

    @browsing
    def test_mail_serialization_contains_reference_number(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.mail, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json.get(u'reference_number'), u'Client1 1.1 / 1 / 15')
