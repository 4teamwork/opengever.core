from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import Unauthorized


class TestDossierWorkflow(IntegrationTestCase):

    def test_deleting_dossier_is_only_allowed_for_managers(self):
        self.login(self.dossier_manager)
        self.assert_has_not_permissions(["Delete objects"], self.dossier)
        with self.assertRaises(Unauthorized):
            api.content.delete(obj=self.dossier)
        self.login(self.manager)
        self.assert_has_permissions(["Delete objects"], self.dossier)

    @staticmethod
    def get_action_menu_content():
        editbar.menu("Actions")
        actions = editbar.menu("Actions").css("li")
        return [el.text for el in actions]

    @browsing
    def test_offer_transition_is_hidden_in_action_menu(self, browser):
        self.login(self.manager, browser)
        browser.visit(self.expired_dossier)
        expected = ['Cover (PDF)', 'Export as Zip',
                    'Print details (PDF)', 'Properties', 'Sharing',
                    'Policy...']
        self.assertItemsEqual(expected, self.get_action_menu_content())

    @browsing
    def test_archive_transition_is_hidden_in_action_menu(self, browser):
        self.login(self.dossier_manager, browser)
        browser.visit(self.dossier)
        expected = ['Cover (PDF)', 'Export as Zip', 'Print details (PDF)',
                    'Properties', 'dossier-transition-deactivate']
        self.assertItemsEqual(expected, self.get_action_menu_content())

    @browsing
    def test_available_actions_in_action_menu_for_managers(self, browser):
        self.login(self.manager, browser)
        browser.visit(self.dossier)
        expected = ['Cover (PDF)', 'Export as Zip', 'Print details (PDF)',
                    'Properties', 'Sharing', 'dossier-transition-deactivate',
                    'dossier-transition-resolve', 'Policy...']
        self.assertItemsEqual(expected, self.get_action_menu_content())
