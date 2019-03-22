from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
from plonetheme.teamraum.testing import TeamraumThemeTestCase
from Products.CMFCore.utils import getToolByName
import transaction


class TestPersonalBar(TeamraumThemeTestCase):

    @browsing
    def test_no_language_link_by_default(self, browser):
        browser.login().visit(self.portal)
        self.assertFalse(
            len(browser.css('#portal-personaltools .category-language')),
            'Expect no language items in personal bar')

    @browsing
    def test_language_switch_is_in_usermenu(self, browser):
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('de')
        language_tool.addSupportedLanguage('en')
        language_tool.use_request_negotiation = True
        transaction.commit()

        browser.login().visit(self.portal)

        self.assertEquals(
            2,
            len(browser.css('#portal-personaltools .category-language')),
            'Expect 2 language links in personal bar')

        self.assertEquals(
            0,
            browser.css('#portal-personaltools li').text.index('English'),
            'Expect "English" in first position')

        self.assertEquals(
            1,
            browser.css('#portal-personaltools li').text.index('Deutsch'),
            'Expect "Deutsch" in second position')

        self.assertEquals(
            'http://nohost/plone/switchLanguage?set_language=en',
            browser.css('#portal-personaltools li a').first.attrib['href'])

        self.assertEquals(
            'http://nohost/plone/switchLanguage?set_language=de',
            browser.css('#portal-personaltools li a')[1].attrib['href'])

        self.assertIn(
            'separator',
            browser.css(
                '#portal-personaltools .category-language')[-1].attrib['class'],
            'Expect separator css class on the last language item.')


class TestWebactionsInPersonalBar(IntegrationTestCase):

    def setUp(self):
        super(TestWebactionsInPersonalBar, self).setUp()

        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5,
                       enabled=True,
                       display='user-menu'))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=1,
                       enabled=True,
                       display='user-menu',
                       target_url="http://example.org/endpoint2"))

    @browsing
    def test_webactions_are_shown_in_usermenu(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.dossier)

        webactions = browser.css('#portal-personaltools .category-webactions > a')

        self.assertEqual(2, len(webactions),
                         'Expect 2 webaction links in personal bar')

        self.assertEqual(['Action 2', 'Action 1'], webactions.text)

        self.assertEqual(
            map(lambda item: item.get("href"), webactions),
            ['http://example.org/endpoint2', 'http://example.org/endpoint'])

    @browsing
    def test_only_webactions_with_display_user_menu_are_shown_in_usermenu(self, browser):
        self.login(self.regular_user, browser)
        storage = get_storage()
        storage.update(0, {"display": "actions-menu"})

        browser.visit(self.dossier)
        webactions = browser.css('#portal-personaltools .category-webactions > a')

        self.assertEqual(1, len(webactions),
                         'Expect 1 webaction link in personal bar')

        self.assertEqual(['Action 2'], webactions.text)
