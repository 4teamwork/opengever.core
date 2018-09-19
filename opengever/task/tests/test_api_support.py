from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.testing import IntegrationTestCase
import json


class TestAPISupport(IntegrationTestCase):

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    @browsing
    def test_adding_a_task(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            "@type": "opengever.task.task",
            "title": "Task",
            "task_type": "correction",
            "text": "Anweisungen etc.",
            "responsible": self.regular_user.id,
            "issuer": self.secretariat_user.id,
            "responsible_client": "fa"}

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url(),
                         method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        task = children['added'].pop()

        self.assertEqual('Task', task.title)
        self.assertEqual('correction', task.task_type)
        self.assertEqual('fa', task.responsible_client)
        self.assertEqual(self.regular_user.id, task.responsible)
        self.assertEqual(self.secretariat_user.id, task.issuer)

    @browsing
    def test_added_task_is_indexed_in_globalindex(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            "@type": "opengever.task.task",
            "title": "Task",
            "task_type": "correction",
            "text": "Anweisungen etc.",
            "responsible": self.regular_user.id,
            "issuer": self.secretariat_user.id,
            "responsible_client": "fa"}

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url(),
                         method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        sql_task = children['added'].pop().get_sql_object()

        self.assertEqual('Task', sql_task.title)
        self.assertEqual('correction', sql_task.task_type)
        self.assertEqual('fa', sql_task.assigned_org_unit)
        self.assertEqual(self.regular_user.id, sql_task.responsible)
        self.assertEqual(self.secretariat_user.id, sql_task.issuer)

    @browsing
    def test_watchers_are_correclty_registered(self, browser):
        self.activate_feature('activity')

        self.login(self.regular_user, browser=browser)

        data = {
            "@type": "opengever.task.task",
            "title": "Task",
            "task_type": "correction",
            "text": "Anweisungen etc.",
            "responsible": self.regular_user.id,
            "issuer": self.secretariat_user.id,
            "responsible_client": "fa"}

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier.absolute_url(),
                         method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        task = children['added'].pop()
        watchers = notification_center().get_watchers(task)

        self.assertEqual([u'kathi.barfuss', u'jurgen.konig'],
                         [watcher.actorid for watcher in watchers])
