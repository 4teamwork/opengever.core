from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


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
        self.assertEquals(u'We apologize for the inconvenience, but the page '
                          u'you were trying to access is not at this '
                          u'address.\n\nPlease contact the responsible person '
                          u'if this problem persists.\n\nBack to the portal',
                          browser.css('.error-body').first.text)

    @browsing
    def test_plone_redirector_still_works(self, browser):
        self.login(self.regular_user, browser)
        cb = self.subdossier.manage_cutObjects(self.subdocument.id)
        self.empty_dossier.manage_pasteObjects(cb)

        browser.visit(self.document)
        self.assertEquals(self.document.absolute_url(),
                          browser.url)

    @browsing
    def test_exception_while_publish_shows_custom_error_page(self, browser):
        self.login(self.regular_user, browser)
        url = self.dossier.absolute_url() + '?foo:int=not_a_int'
        with browser.expect_http_error(code=500):
            browser.open(url)

        self.assertTrue(browser.css('#content.gever-error-page'),
                        'Expect to be on the gever error page')
        self.assertEquals(u'We\u2019re sorry, but there seems to be an '
                          u'error\u2026',
                          browser.css('h1').first.text)

        # The error happens too early the error log is no yet available
        self.assertEquals(u'Please contact the responsible person if this '
                          u'problem persists.',
                          browser.css('.error-body').first.text)

    @browsing
    def test_show_error_number_to_user_for_regular_errors(self, browser):
        self.login(self.regular_user, browser)

        # Provoke a AttributeError by calling the breadcrumb_by_uid view
        # without a uid
        with browser.expect_http_error(code=500):
            browser.open(view='breadcrumb_by_uid')

        self.assertTrue(browser.css('#content.gever-error-page'),
                        'Expect to be on the gever error page')
        self.assertEquals(u'We\u2019re sorry, but there seems to be an '
                          u'error\u2026',
                          browser.css('h1').first.text)

        self.assertTrue(browser.css('.error-body').first.text.startswith(
            u'The error has been logged as entry number'))

    @browsing
    def test_show_traceback_to_managers_for_regular_errors(self, browser):
        self.login(self.manager, browser)

        # Provoke a AttributeError by calling the breadcrumb_by_uid view
        # without a uid
        with browser.expect_http_error(code=500):
            browser.open(view='breadcrumb_by_uid')

        self.assertTrue(browser.css('#content.gever-error-page'),
                        'Expect to be on the gever error page')
        self.assertEquals(u'We\u2019re sorry, but there seems to be an '
                          u'error\u2026',
                          browser.css('h1').first.text)

        self.assertTrue(browser.css('.traceback').first.text.startswith(
            'Traceback (most recent call last):'))


class TestErrorPageFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestErrorPageFunctional, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_read_only_error_shows_custom_error_page(self, browser):
        browser.login().open(self.dossier)

        with ZODBStorageInReadonlyMode():
            factoriesmenu.add('Document')
            with browser.expect_http_error(code=500):
                browser.fill({'Title': u'Foo'}).save()

        self.assertEqual(
            'Error: Unexpected write attempt during ReadOnly mode',
            browser.css('h1').first.text)

        self.assertEqual(0, len(self.dossier.objectValues()))
