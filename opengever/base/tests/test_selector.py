from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestLanguageSelectorMenu(FunctionalTestCase):

    def setUp(self):
        super(TestLanguageSelectorMenu, self).setUp()
        tool = api.portal.get_tool('portal_languages')
        tool.addSupportedLanguage('de')
        tool.addSupportedLanguage('fr')
        tool.setDefaultLanguage('de')

        transaction.commit()

    @browsing
    def test_list_all_available_languages(self, browser):
        browser.login().open(self.portal)
        self.assertEquals(['English', 'Deutsch', u'Fran\xe7ais'],
                          browser.css('dl#portal-languageselector dd li').text)

    @browsing
    def test_title_contains_current_language(self, browser):
        browser.login().open(self.portal)
        title = browser.css('dl#portal-languageselector dt').first
        self.assertEquals('Deutsch', title.text)

    @browsing
    def test_current_language_is_marked_as_currentLanguage(self, browser):
        browser.login().open(self.portal)
        self.assertEquals(
            ['Deutsch'],
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
