from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestAddFromDocugateTemplate(IntegrationTestCase):

    features = ("officeconnector-checkout", "docugate")

    @browsing
    def test_docugate_add_form(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Document from Docugate template')
        browser.fill({'Title': 'My Docugate document'})
        browser.click_on('Save')

        self.assertEqual(browser.context.Title(), 'My Docugate document')
        self.assertTrue(browser.context.is_shadow_document())
        self.assertIn("window.location = 'oc:", browser.css('.redirector').first.text)
