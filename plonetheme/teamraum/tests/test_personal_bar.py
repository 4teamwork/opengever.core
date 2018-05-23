from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plonetheme.teamraum.testing import TEAMRAUMTHEME_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase

import transaction


class TestSearchBoxViewlet(TestCase):

    layer = TEAMRAUMTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

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
