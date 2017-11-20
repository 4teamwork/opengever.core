# -*- coding: utf-8 -*-

from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.contact.interfaces import IContactFolder
from opengever.testing import add_languages
from opengever.testing import IntegrationTestCase


class TestContactFolder(IntegrationTestCase):

    def setUp(self):
        super(TestContactFolder, self).setUp()
        add_languages(['de-ch', 'fr-ch'])

    def test_provides_marker_interface(self):
        self.login(self.manager)
        self.assertTrue(IContactFolder.providedBy(self.contactfolder))

    @browsing
    def test_supports_translated_title(self, browser):
        self.login(self.manager, browser=browser)

        browser.open()
        factoriesmenu.add('ContactFolder')
        browser.fill({'Title (German)': u'Kontakte',
                      'Title (French)': u'Contacts'})
        browser.find('Save').click()

        browser.find(u'Français').click()
        self.assertEquals(u"Contacts", browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals("Kontakte", browser.css('h1').first.text)

    def test_portlets_inheritance_is_blocked(self):
        self.login(self.manager)

        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', self.contactfolder)
