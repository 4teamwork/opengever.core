from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestLanguageSelectorMenu(FunctionalTestCase):

    def setUp(self):
        super(TestLanguageSelectorMenu, self).setUp()
        tool = api.portal.get_tool('portal_languages')
        tool.use_combined_language_codes = True
        tool.addSupportedLanguage('de-ch')
        tool.addSupportedLanguage('fr-ch')
        tool.setDefaultLanguage('de-ch')

        transaction.commit()

    @browsing
    def test_list_all_available_languages(self, browser):
        browser.login().open(self.portal)
        self.assertEquals(['English', 'DE', 'FR'],
                          browser.css('dl#portal-languageselector dd li').text)

    @browsing
    def test_title_contains_current_language(self, browser):
        browser.login().open(self.portal)
        title = browser.css('dl#portal-languageselector dt').first
        self.assertEquals('DE', title.text)

    @browsing
    def test_current_language_is_marked_as_currentLanguage(self, browser):
        browser.login().open(self.portal)
        self.assertEquals(
            ['DE'],
            browser.css('dl#portal-languageselector dd li.currentLanguage').text)

    @browsing
    def test_change_current_language(self, browser):
        browser.login().open(self.portal)

        link = browser.css('dl#portal-languageselector dd a').first

        self.assertEquals('English', link.text)
        link.click()

        self.assertEquals(
            ['English'],
            browser.css('dl#portal-languageselector dd li.currentLanguage').text)
