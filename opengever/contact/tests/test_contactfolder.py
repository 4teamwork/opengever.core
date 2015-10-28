from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestContactFolder(FunctionalTestCase):

    def setUp(self):
        super(TestContactFolder, self).setUp()
        self.grant('Manager')

        add_languages(['de-ch', 'fr-ch'])

    @browsing
    def test_supports_translated_title(self, browser):
        browser.login().open()
        factoriesmenu.add('ContactFolder')
        browser.fill({'Title (German)': u'Kontakte',
                      'Title (French)': u'Contacts'})
        browser.find('Save').click()

        browser.find('FR').click()
        self.assertEquals(u"Contacts", browser.css('h1').first.text)

        browser.find('DE').click()
        self.assertEquals("Kontakte", browser.css('h1').first.text)
