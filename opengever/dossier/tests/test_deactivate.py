from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


class TestDossierDeactivation(IntegrationTestCase):

    @browsing
    def test_fails_with_resolved_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('dossier-state-resolved', self.subdossier)
        browser.open(self.dossier, view='transition-deactivate',
                     send_authenticator=True)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        statusmessages.assert_message(
            u"The Dossier can\'t be deactivated,"
            u" the subdossier 2016 is already resolved")

    @browsing
    def test_fails_with_checked_out_documents(self, browser):
        self.login(self.dossier_responsible, browser)
        getMultiAdapter((self.document, self.request),
                        ICheckinCheckoutManager).checkout()
        browser.open(self.dossier, view='transition-deactivate',
                     send_authenticator=True)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        statusmessages.assert_message(
            u"The Dossier can't be deactivated, not all containeddocuments"
            u" are checked in.")

    @browsing
    def test_not_possible_with_not_closed_tasks(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assert_workflow_state('task-state-in-progress', self.task)
        browser.open(self.dossier, view='transition-deactivate',
                     send_authenticator=True)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        statusmessages.assert_message(
            u"The Dossier can't be deactivated, not all contained"
            u" tasks are in a closed state.")

    @browsing
    def test_not_possible_with_active_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assert_workflow_state('proposal-state-active', self.proposal)
        browser.open(self.dossier, view='transition-deactivate',
                     send_authenticator=True)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        statusmessages.assert_message(
            u"The Dossier can't be deactivated,"
            u" not all contained tasks are in a closed state.")

    @browsing
    def test_recursively_deactivate_subdossier(self, browser):
        self.login(self.secretariat_user, browser)
        subdossier = create(Builder('dossier').within(self.empty_dossier))
        browser.open(self.empty_dossier)
        editbar.menu_option('Actions', 'dossier-transition-deactivate').click()
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)
        self.assert_workflow_state('dossier-state-inactive', subdossier)

    @browsing
    def test_already_inactive_subdossier_will_be_ignored(self, browser):
        self.login(self.secretariat_user, browser)
        subdossier = create(Builder('dossier').within(self.empty_dossier)
                            .in_state('dossier-state-inactive'))
        browser.open(self.empty_dossier)
        editbar.menu_option('Actions', 'dossier-transition-deactivate').click()
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)
        self.assert_workflow_state('dossier-state-inactive', subdossier)

    @browsing
    def test_sets_end_date_to_current_date(self, browser):
        self.login(self.secretariat_user, browser)
        with freeze(datetime(2016, 3, 29)):
            browser.open(self.empty_dossier)
            editbar.menu_option('Actions', 'dossier-transition-deactivate').click()

        self.assertEqual(date(2016, 3, 29), IDossier(self.empty_dossier).end)
