from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestLanguageNegotiation(IntegrationTestCase):

    def setUp(self):
        super(TestLanguageNegotiation, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @browsing
    def test_request_lang_nego_works_with_simple_lang_codes(self, browser):
        self.login(self.regular_user, browser=browser)

        # Site default language is de-ch
        # But we should be able to request French, even with a simple code
        browser.open(headers={'Accept-Language': 'fr'})

        html = browser.css('html').first
        self.assertEqual('fr-ch', html.attrib['lang'])

        self.assertIn('language-fr-ch',
                      browser.css('.currentLanguage').first.classes)

    @browsing
    def test_request_lang_nego_works_with_combined_lang_codes(self, browser):
        self.login(self.regular_user, browser=browser)

        # Site default language is de-ch
        # But we should be able to request French using a combined code
        browser.open(headers={'Accept-Language': 'fr-ch'})

        html = browser.css('html').first
        self.assertEqual('fr-ch', html.attrib['lang'])

        self.assertIn('language-fr-ch',
                      browser.css('.currentLanguage').first.classes)
