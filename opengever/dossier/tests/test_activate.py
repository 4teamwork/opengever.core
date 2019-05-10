from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase


class TestDossierActivation(IntegrationTestCase):

    @browsing
    def test_recursively_activates_subdossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state(
            'dossier-state-inactive',
            self.dossier,
            self.subdossier,
            self.subdossier2,
            self.subsubdossier,
            )

        browser.open(self.dossier)
        editbar.menu_option('Actions', 'dossier-transition-activate').click()
        statusmessages.assert_message('The Dossier has been activated')

        self.assert_workflow_state('dossier-state-active', self.dossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier2)
        self.assert_workflow_state('dossier-state-active', self.subsubdossier)

    @browsing
    def test_activate_subdossier_is_disallowed_when_main_dossier_is_inactive(
            self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-inactive',
                                self.dossier, self.subdossier)
        browser.open(self.subdossier, view='transition-activate',
                     send_authenticator=True)
        statusmessages.assert_message("This subdossier can't be activated,"
                                      "because the main dossiers is inactive")
        self.assert_workflow_state('dossier-state-inactive', self.subdossier)

    @browsing
    def test_resets_end_dates_recursively(self, browser):
        self.login(self.secretariat_user, browser)
        IDossier(self.dossier).end = date(2013, 2, 21)
        IDossier(self.subdossier).end = date(2013, 2, 21)
        IDossier(self.subsubdossier).end = date(2013, 2, 21)

        self.set_workflow_state(
            'dossier-state-inactive',
            self.dossier,
            self.subdossier,
            self.subdossier2,
            self.subsubdossier,
            )
        self.assertIsNotNone(IDossier(self.dossier).end)
        self.assertIsNotNone(IDossier(self.subdossier).end)
        self.assertIsNotNone(IDossier(self.subsubdossier).end)

        browser.open(self.dossier)
        editbar.menu_option('Actions', 'dossier-transition-activate').click()
        self.assert_workflow_state('dossier-state-active', self.dossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier)
        self.assert_workflow_state('dossier-state-active', self.subsubdossier)
        self.assertIsNone(IDossier(self.dossier).end)
        self.assertIsNone(IDossier(self.subdossier).end)
        self.assertIsNone(IDossier(self.subsubdossier).end)

    @browsing
    def test_end_date_is_reindexed(self, browser):
        self.login(self.secretariat_user, browser)
        enddate = date(2016, 12, 31)
        enddate_index_value = self.dateindex_value_from_datetime(enddate)

        self.assertEqual(enddate, IDossier(self.inactive_dossier).end)
        self.assert_index_value(enddate_index_value, 'end', self.inactive_dossier)
        self.assert_metadata_value(enddate, 'end', self.inactive_dossier)

        browser.open(self.inactive_dossier)
        editbar.menu_option('Actions', 'dossier-transition-activate').click()

        self.assert_index_value('', 'end', self.inactive_dossier)
        self.assert_metadata_value(None, 'end', self.inactive_dossier)
