from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.task import is_private_task_feature_enabled
from opengever.testing import IntegrationTestCase


class TestPrivateTaskIntegration(IntegrationTestCase):

    @browsing
    def test_feature_is_activated_by_default(self, browser):
        self.assertTrue(is_private_task_feature_enabled())

    @browsing
    def test_is_private_field_is_deactivated_by_default(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.dossier)
        factoriesmenu.add('Task')

        self.assertFalse(
            browser.css('#form-widgets-is_private input').first.checked)

    @browsing
    def test_is_private_field_is_hidden_in_edit_form(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.visit(self.task, view="edit")

        self.assertEqual(
            'hidden',
            browser.css('#formfield-form-widgets-is_private input').first.type)


class TestPrivateTaskDeactivatedIntegration(IntegrationTestCase):

    features = ('!private-tasks', )

    @browsing
    def test_feature_is_deactivated(self, browser):
        self.assertFalse(is_private_task_feature_enabled())

    @browsing
    def test_is_private_field_is_hidden_in_add_form(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.dossier)
        factoriesmenu.add('Task')

        self.assertEqual(
            'hidden',
            browser.css('#formfield-form-widgets-is_private input').first.type)

    @browsing
    def test_is_private_field_is_hidden_in_edit_form(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.visit(self.task, view="edit")

        self.assertEqual(
            'hidden',
            browser.css('#formfield-form-widgets-is_private input').first.type)
