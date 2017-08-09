from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestErrorPage(IntegrationTestCase):

    @browsing
    def test_not_found_shows_custom_error_page(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=404):
            browser.visit(self.dossier, view='thisviewdoesnotexist')

        self.assertTrue(browser.css('#content.gever-error-page'),
                        'Expect to be on the gever error page')
        self.assertEquals(u'This page does not seem to exist\u2026',
                          browser.css('h1').first.text)
        self.assertEquals(u'We apologize for the inconvenience, but the page'
                          u' you were trying to access is not at this address.'
                          u'\n\nIf you are certain you have the correct web '
                          u'address but are encountering an error, please '
                          u'contact the Site Administration.\n\nThank you.',
                          browser.css('.error-body').first.text)

    @browsing
    def test_plone_redirector_still_works(self, browser):
        self.login(self.regular_user, browser)
        cb = self.subdossier.manage_cutObjects(self.subdocument.id)
        self.empty_dossier.manage_pasteObjects(cb)

        browser.visit(self.document)
        self.assertEquals(self.document.absolute_url(),
                          browser.url)
