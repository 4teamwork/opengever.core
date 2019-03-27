from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages import factoriesmenu
from opengever.task import is_private_task_feature_enabled
from opengever.testing import IntegrationTestCase
import json


class TestPrivateTaskIntegration(IntegrationTestCase):

    def test_feature_is_activated_by_default(self):
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

    @browsing
    def test_task_private_field_cant_be_changed_in_edit_form(self, browser):
        self.login(self.administrator, browser=browser)
        self.assertFalse(self.seq_subtask_1.is_private)

        browser.open(self.seq_subtask_1, view='edit')
        browser.fill({'form.widgets.is_private:list': 'selected'})
        browser.click_on('Save')

        self.assertFalse(self.seq_subtask_1.is_private)


class TestPrivateTaskDeactivatedIntegration(IntegrationTestCase):

    features = ('!private-tasks', )

    def test_feature_is_deactivated(self):
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

    @browsing
    def test_cant_create_private_tasks_when_feature_is_inactive(self, browser):
        self.login(self.dossier_responsible, browser)

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, view='++add++opengever.task.task')
            browser.fill({'Title': u'I should not be private despite input.',
                          'Task Type': 'comment',
                          'form.widgets.is_private:list': 'selected'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(
                'fa:{}'.format(self.secretariat_user.getId()))
            browser.css('#form-buttons-save').first.click()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertEqual(['The private task feature is disabled'],
                         browser.css('form .error').text)
        self.assertEqual(0, len(children['added']))

    @browsing
    def test_cant_create_private_tasks_over_api_when_feature_is_inactive(self, browser):
        self.login(self.dossier_responsible, browser)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = json.dumps({
            "@type": "opengever.task.task",
            "title": "I should not be private despite input",
            "task_type": "comment",
            "issuer": self.dossier_responsible.getId(),
            "responsible": self.secretariat_user.getId(),
            "responsible_client": 'fa',
            "is_private": True,
        })

        with browser.expect_http_error(400):
            browser.open(self.dossier, headers=headers, data=data)
