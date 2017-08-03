# -*- coding: utf-8 -*-

from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.contact.interfaces import IContactFolder
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase


class TestContactFolder(FunctionalTestCase):

    def setUp(self):
        super(TestContactFolder, self).setUp()
        self.grant('Manager')

        add_languages(['de-ch', 'fr-ch'])

    def test_provides_marker_interface(self):
        contactfolder = create(Builder('contactfolder'))
        self.assertTrue(IContactFolder.providedBy(contactfolder))

    @browsing
    def test_supports_translated_title(self, browser):
        browser.login().open()
        factoriesmenu.add('ContactFolder')
        browser.fill({'Title (German)': u'Kontakte',
                      'Title (French)': u'Contacts'})
        browser.find('Save').click()

        browser.find(u'Français').click()
        self.assertEquals(u"Contacts", browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals("Kontakte", browser.css('h1').first.text)

    @browsing
    def test_portlets_inheritance_is_blocked(self, browser):
        browser.login().open()
        factoriesmenu.add('ContactFolder')
        browser.fill({'Title (German)': u'Kontakte',
                      'Title (French)': u'Contacts'})
        browser.find('Save').click()

        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', browser.context)
