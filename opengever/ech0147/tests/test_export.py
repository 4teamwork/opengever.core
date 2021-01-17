from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
from zipfile import ZipFile
from StringIO import StringIO
from zope.annotation.interfaces import IAnnotations
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY


class TestExport(IntegrationTestCase):

    @browsing
    def test_actions_menu_doesnt_contain_ech0147_export_if_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        actions = browser.css(
            '#plone-contentmenu-actions .actionMenuContent .subMenuTitle'
            ).text
        self.assertNotIn('eCH-0147 export', actions)

    @browsing
    def test_actions_menu_contains_ech0147_export(self, browser):
        self.activate_feature('ech0147-export')
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        actions = browser.css(
            '#plone-contentmenu-actions .actionMenuContent .subMenuTitle'
            ).text
        self.assertIn('eCH-0147 export', actions)

    @browsing
    def test_export_dossier_if_disabled_returns_404(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=404):
            browser.open(self.dossier, view='ech0147_export')

    @browsing
    def test_export_dossier_returns_ech0147_zipfile(self, browser):
        self.activate_feature('ech0147-export')
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='ech0147_export')
        browser.forms['form'].fill(
            {'Action': 'new', 'Priority': 'undefined'}).submit()
        self.assertEqual(browser.headers['content-type'], 'application/zip')
        zipfile = ZipFile(StringIO(browser.contents))
        contents = zipfile.namelist()
        self.assertIn('header.xml', contents)
        self.assertIn('message.xml', contents)

    @browsing
    def test_cancel_redirects_to_context(self, browser):
        self.activate_feature('ech0147-export')
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='ech0147_export')
        browser.forms['form'].find('Cancel').click()
        self.assertEqual(browser.url, self.dossier.absolute_url())

    @browsing
    def test_export_dossier_creates_journal_entry(self, browser):
        self.activate_feature('ech0147-export')
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='ech0147_export')
        browser.forms['form'].fill(
            {'Action': 'new', 'Priority': 'undefined'}).submit()
        journal = IAnnotations(self.dossier).get(
            JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        self.assertEqual(journal[-1]['action']['type'], 'eCH-0147 Export')

    @browsing
    def test_export_dossier_without_required_fields_renders_errors(self, browser):
        self.activate_feature('ech0147-export')
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='ech0147_export')
        browser.forms['form'].submit()
        self.assertIn('Error', browser.contents)
