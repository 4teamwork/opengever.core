from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.testing import IntegrationTestCase
from plone import api


class TestIntegrationTestCase(IntegrationTestCase):

    def test_login(self):
        self.assertTrue(api.user.is_anonymous())
        self.login(self.regular_user)
        self.assertFalse(api.user.is_anonymous())
        self.assertEqual(self.regular_user, api.user.get_current())

    @browsing
    def test_login_browser(self, browser):
        with browser.expect_unauthorized():
            browser.open()
        self.assertFalse(plone.logged_in())
        self.login(self.regular_user, browser)
        browser.open()
        self.assertEquals(self.regular_user.getProperty('fullname'),
                          plone.logged_in().encode('utf-8'))

    def test_login_as_context_manager(self):
        self.assertTrue(api.user.is_anonymous())

        with self.login(self.regular_user):
            self.assertFalse(api.user.is_anonymous())
            self.assertEqual(self.regular_user, api.user.get_current())

            with self.login(self.administrator):
                self.assertFalse(api.user.is_anonymous())
                self.assertEqual(self.administrator, api.user.get_current())

            self.assertFalse(api.user.is_anonymous())
            self.assertEqual(self.regular_user, api.user.get_current())

        self.assertTrue(api.user.is_anonymous())

    @browsing
    def test_login_as_context_manager_in_browser(self, browser):
        with browser.expect_unauthorized():
            browser.open()
        self.assertFalse(plone.logged_in())

        with self.login(self.regular_user, browser):
            browser.open()
            self.assertEquals(self.regular_user.getProperty('fullname'),
                              plone.logged_in().encode('utf-8'))

            with self.login(self.administrator, browser):
                browser.open()
                self.assertEquals(self.administrator.getProperty('fullname'),
                                  plone.logged_in().encode('utf-8'))

            browser.open()
            self.assertEquals(self.regular_user.getProperty('fullname'),
                              plone.logged_in().encode('utf-8'))

        with browser.expect_unauthorized():
            browser.open()
        self.assertFalse(plone.logged_in())

    def test_get_catalog_indexdata(self):
        self.login(self.regular_user)
        self.maxDiff = None
        self.assertDictContainsSubset(
            {'Type': u'Business Case Dossier',
             'sortable_title': 'vertrage mit der kantonalen...verwaltung'},
            self.get_catalog_indexdata(self.dossier))

    def test_get_catalog_metadata(self):
        self.login(self.regular_user)
        self.maxDiff = None
        self.assertDictContainsSubset(
            {'Type': 'Business Case Dossier',
             'Title': 'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung'},
            self.get_catalog_metadata(self.dossier))

    def test_set_workflow_state(self):
        self.login(self.dossier_responsible)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier)

        self.set_workflow_state('dossier-state-inactive',
                                self.dossier, self.subdossier)
        self.assert_workflow_state('dossier-state-inactive', self.dossier)
        self.assert_workflow_state('dossier-state-inactive', self.subdossier)
