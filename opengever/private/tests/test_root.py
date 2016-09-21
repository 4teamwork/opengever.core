from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized


class TestPrivateRoot(FunctionalTestCase):

    @browsing
    def test_is_addable_on_plone_site(self, browser):
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Private Root')
        browser.fill({'Title (German)': u'Meine Ablage',
                      'Title (French)': u'Mon d\xe9p\xf4t'})
        browser.click_on('Save')

        self.assertEquals(['Meine Ablage'], browser.css('h1').text)

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.portal, view='++add++opengever.private.root')
            browser.fill({'Title (German)': u'Meine Ablage',
                          'Title (French)': u'Mon d\xe9p\xf4t'})
            browser.click_on('Save')
