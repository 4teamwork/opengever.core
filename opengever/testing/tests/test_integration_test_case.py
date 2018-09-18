from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
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

    def test_extjs_is_disabled_by_default(self):
        """ExtJS is disabled by default in the integration test case,
        so that tabbedview listings render the table as simple HTML,
        which is testable with the testbrowser.
        """
        self.assertFalse(api.portal.get_registry_record(
            'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'))

    def test_features_can_be_enabled(self):
        """Test parse_feature() can enable a setting disabled per default."""
        self.assertFalse(
            api.portal.get_registry_record('is_feature_enabled', interface=IGeverBumblebeeSettings),
            'This test blindly assumes Bumblebee to be off per default.',
        )
        self.parse_feature('bumblebee')
        self.assertTrue(api.portal.get_registry_record('is_feature_enabled', interface=IGeverBumblebeeSettings))

    def test_features_can_be_disabled(self):
        """Test parse_feature() can disable a setting enabled per default."""
        self.assertTrue(
            api.portal.get_registry_record('attach_to_outlook_enabled', interface=IOfficeConnectorSettings),
            "This test blindly assumes 'Attach to email' to be on per default.",
        )
        self.parse_feature('!officeconnector-attach')
        self.assertFalse(
            api.portal.get_registry_record('attach_to_outlook_enabled', interface=IOfficeConnectorSettings),
        )

    def test_extjs_can_be_enabled_as_feature(self):
        """In order for actually testing ExtJS behavior, ExtJS can be enabled
        like a feature.
        """
        self.assertFalse(api.portal.get_registry_record(
            'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'))
        self.activate_feature('extjs')
        self.assertTrue(api.portal.get_registry_record(
            'ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'))
