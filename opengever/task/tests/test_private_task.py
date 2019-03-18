from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.task import is_private_task_feature_enabled
from opengever.testing import IntegrationTestCase
from plone.protect import createToken
from requests_toolbelt.utils import formdata
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
    def test_is_private_field_is_not_present_in_edit_form(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.open(self.task, view="edit")
        self.assertIsNone(
            browser.css('#formfield-form-widgets-is_private input')
            .first_or_none,
        )

    @browsing
    def test_task_private_field_cant_be_changed_through_edit_form(self, browser):
        self.login(self.administrator, browser=browser)
        self.assertFalse(self.seq_subtask_1.is_private)

        # We play malicious here to verify the field validation works
        form_data = formdata.urlencode({
            'fieldset.current': '#fieldsetlegend-default',
            'form.widgets.title': self.seq_subtask_1.title,
            'form.widgets.issuer': self.seq_subtask_1.issuer,
            'form.widgets.task_type': 'direct-execution',
            'form.widgets.responsible_client:list': self.seq_subtask_1.responsible_client,
            'form.widgets.responsible': '{}:{}'.format(
                self.seq_subtask_1.responsible_client,
                self.seq_subtask_1.responsible,
            ),
            'form.widgets.is_private:list': 'selected',
            'form.widgets.deadline': self.seq_subtask_1.deadline.strftime('%d.%m.%Y'),
            'form.buttons.save': 'Speichern',
            '_authenticator': createToken(),
        })

        browser.open(
            self.seq_subtask_1,
            view='@@edit',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=form_data,
        )
        self.assertEqual(['There were some errors.'], error_messages())
        self.assertFalse(self.seq_subtask_1.is_private)

    @browsing
    def test_can_create_private_tasks_over_api(self, browser):
        self.login(self.dossier_responsible, browser)

        with self.observe_children(self.dossier) as children:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            data = json.dumps({
                "@type": "opengever.task.task",
                "title": "I should be private",
                "task_type": "comment",
                "issuer": self.dossier_responsible.getId(),
                "responsible": self.secretariat_user.getId(),
                "responsible_client": 'fa',
                "is_private": True,
            })
            browser.open(self.dossier, headers=headers, data=data)

        task = children['added'].pop()
        self.assertEqual('I should be private', task.title)
        self.assertTrue(task.is_private)


class TestPrivateTaskDeactivatedIntegration(IntegrationTestCase):

    features = ('!private-tasks', )

    def test_feature_is_deactivated(self):
        self.assertFalse(is_private_task_feature_enabled())

    @browsing
    def test_is_private_field_is_not_present_in_add_form(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.dossier)
        factoriesmenu.add('Task')
        self.assertIsNone(
            browser.css('#formfield-form-widgets-is_private input')
            .first_or_none,
        )

    @browsing
    def test_is_private_field_is_not_present_in_edit_form(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('task-state-open', self.task)
        browser.open(self.task, view="edit")
        self.assertIsNone(
            browser.css('#formfield-form-widgets-is_private input')
            .first_or_none,
        )

    @browsing
    def test_cant_create_private_tasks_when_feature_is_inactive(self, browser):
        self.login(self.dossier_responsible, browser)

        with self.observe_children(self.dossier) as children:
            # We play malicious here to verify the field validation works
            form_data = formdata.urlencode({
                'fieldset.current': '#fieldsetlegend-default',
                'form.widgets.title': 'Foo bar',
                'form.widgets.issuer': self.dossier_responsible.getId(),
                'form.widgets.task_type': 'direct-execution',
                'form.widgets.responsible_client:list': 'fa',
                'form.widgets.responsible': 'fa:{}'.format(
                    self.secretariat_user.getId()),
                'form.widgets.is_private:list': 'selected',
                'form.widgets.deadline': '01.01.2020',
                'form.buttons.save': 'Speichern',
                '_authenticator': createToken(),
            })

            browser.open(
                self.dossier,
                view='++add++opengever.task.task',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=form_data,
            )

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertEqual(set(), children['added'])

    @browsing
    def test_cant_create_private_tasks_over_api_when_feature_is_inactive(self, browser):
        self.login(self.dossier_responsible, browser)

        with self.observe_children(self.dossier) as children:
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
            browser.open(self.dossier, headers=headers, data=data)

        task = children['added'].pop()
        self.assertEqual('I should not be private despite input', task.title)
        self.assertFalse(task.is_private)
