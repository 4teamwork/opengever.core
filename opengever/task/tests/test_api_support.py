from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.task.adapters import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api
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


class TestAPITransitions(IntegrationTestCase):

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    @browsing
    def test_transition_changes_adds_response(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@workflow/task-transition-open-in-progress'.format(
            self.seq_subtask_1.absolute_url())
        data = {'text': 'Wird gemacht!'}

        browser.open(url, method='POST', data=json.dumps(data), headers=self.api_headers)

        self.assertEqual('task-state-in-progress',
                         api.content.get_state(self.seq_subtask_1))
        self.assertEqual('task-state-in-progress',
                         self.seq_subtask_1.get_sql_object().review_state)

        response = IResponseContainer(self.seq_subtask_1)[-1]

        self.assertEqual(u'Wird gemacht!', response.text)
        self.assertEqual(u'task-transition-open-in-progress', response.transition)
        self.assertEqual(self.regular_user.id, response.creator)

    @browsing
    def test_validates_schema(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@workflow/task-transition-modify-deadline'.format(
            self.task.absolute_url())

        # Missing
        data = {'text': 'Wird nun dringender.'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        # Invalid
        data = {'text': 'Wird nun dringender.', 'new_deadline': 'not-valid'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

    @browsing
    def test_modify_deadline_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@workflow/task-transition-modify-deadline'.format(
            self.task.absolute_url())

        data = {'text': 'Wird nun dringender.', 'new_deadline': '2019-11-23'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(date(2019, 11, 23), self.task.deadline)

        response = IResponseContainer(self.task)[-1]
        self.assertEqual(
            [{'after': date(2019, 11, 23),
              'id': 'deadline',
              'name': u'label_deadline',
              'before': date(2016, 11, 1)}],
            response.changes)

    @browsing
    def test_close_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@workflow/task-transition-resolved-tested-and-closed'.format(
            self.subtask.absolute_url())

        data = {'text': 'Tiptop, Danke!'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-tested-and-closed',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Tiptop, Danke!', response.text)
        self.assertEqual('task-transition-resolved-tested-and-closed',
                         response.transition)

    @browsing
    def test_close_direct_execution_successful(self, browser):
        self.login(self.regular_user, browser=browser)
        self.subtask.task_type = 'direct-execution'
        self.subtask.sync()
        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-in-progress-tested-and-closed'.format(
            self.subtask.absolute_url())
        browser.open(url, method='POST',
                     data=json.dumps({'text': 'Done!'}), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-tested-and-closed',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Done!', response.text)
        self.assertEqual('task-transition-in-progress-tested-and-closed',
                         response.transition)

    @browsing
    def test_close_information_successful(self, browser):
        self.login(self.regular_user, browser=browser)
        self.subtask.task_type = 'information'
        self.subtask.sync()
        self.set_workflow_state('task-state-open', self.subtask)

        url = '{}/@workflow/task-transition-open-tested-and-closed'.format(
            self.subtask.absolute_url())
        browser.open(url, method='POST', data=json.dumps({'text': 'Done!'}),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-tested-and-closed',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Done!', response.text)
        self.assertEqual('task-transition-open-tested-and-closed',
                         response.transition)

    @browsing
    def test_resolve_successful(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-in-progress-resolved'.format(self.subtask.absolute_url())

        data = {'text': 'Erledigt, siehe Anhang.'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-resolved',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Erledigt, siehe Anhang.', response.text)
        self.assertEqual('task-transition-in-progress-resolved',
                         response.transition)

    @browsing
    def test_reassign_successful(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@workflow/task-transition-reassign'.format(
            self.task.absolute_url())

        data = {'text': 'Not working'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST', data=json.dumps(data), headers=self.api_headers)
        data = {'text': 'Robert macht das.',
                'responsible': self.dossier_responsible.id,
                'responsible_client': u'fa'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(self.dossier_responsible.id, self.task.responsible)
        self.assertEqual('task-state-in-progress', api.content.get_state(self.task))

        response = IResponseContainer(self.task)[-1]
        self.assertEqual(u'Robert macht das.', response.text)
        self.assertEqual('task-transition-reassign', response.transition)

    @browsing
    def test_reassign_to_team_validation(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@workflow/task-transition-reassign'.format(
            self.task.absolute_url())
        data = {'text': 'Robert macht das.',
                'responsible': 'team:1',
                'responsible_client': u'fa'}

        with browser.expect_http_error(400):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

    @browsing
    def test_reassign_admin_unit_change_validation(self, browser):
        self.login(self.regular_user, browser=browser)

        admin_unit, org_unit = self.add_additional_admin_and_org_unit()
        create(Builder('ogds_user')
               .id('james.bond')
               .having(firstname=u'James', lastname=u'Bond')
               .assign_to_org_units([org_unit]))

        url = '{}/@workflow/task-transition-reassign'.format(
            self.task.absolute_url())
        data = {'text': 'Robert macht das.',
                'responsible': 'james.bond',
                'responsible_client': u'rk'}

        with browser.expect_http_error(400):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

    @browsing
    def test_cancel_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-open', self.subtask)

        url = '{}/@workflow/task-transition-open-cancelled'.format(
            self.subtask.absolute_url())
        browser.open(url, method='POST',
                     data=json.dumps({'text': 'Nicht mehr notwendig.'}),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-cancelled',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Nicht mehr notwendig.', response.text)
        self.assertEqual('task-transition-open-cancelled', response.transition)

    @browsing
    def test_reopen_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-cancelled', self.subtask)

        url = '{}/@workflow/task-transition-cancelled-open'.format(
            self.subtask.absolute_url())
        browser.open(url, method='POST',
                     data=json.dumps({'text': u'Brauchen wir trotzdem.'}),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-open',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Brauchen wir trotzdem.', response.text)
        self.assertEqual('task-transition-cancelled-open', response.transition)

    @browsing
    def test_reject_successful(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-open', self.subtask)

        url = '{}/@workflow/task-transition-open-rejected'.format(
            self.subtask.absolute_url())
        data = {'text': u'Kann nicht.'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-rejected',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Kann nicht.', response.text)
        self.assertEqual('task-transition-open-rejected', response.transition)
        self.assertEqual([{'after': self.dossier_responsible.id,
                           'id': 'responsible',
                           'name': u'label_responsible',
                           'before': self.regular_user.id}],
                         response.changes)

    @browsing
    def test_reopen_rejected_task_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-rejected', self.subtask)

        url = '{}/@workflow/task-transition-rejected-open'.format(
            self.subtask.absolute_url())
        data = {'text': u'Dann erledige ich das selbst.'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-open',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Dann erledige ich das selbst.', response.text)
        self.assertEqual('task-transition-rejected-open', response.transition)

    @browsing
    def test_revise_task_successful(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-resolved', self.subtask)

        url = '{}/@workflow/task-transition-resolved-in-progress'.format(
            self.subtask.absolute_url())
        data = {'text': u'Da stimmt was nicht.'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-in-progress',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask)[-1]
        self.assertEqual(u'Da stimmt was nicht.', response.text)
        self.assertEqual('task-transition-resolved-in-progress', response.transition)

    @browsing
    def test_delegate_a_task(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-delegate'.format(
            self.subtask.absolute_url())

        data = {"title": "Neuer Aufgaben Titel",
                "responsibles": ["fa:{}".format(self.meeting_user.id),
                                 "fa:{}".format(self.secretariat_user.id)],
                "issuer": self.dossier_responsible.id,
                "deadline": "2018-12-03"}

        with self.observe_children(self.subtask) as children:
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        tasks = children['added']
        self.assertItemsEqual([self.meeting_user.id, self.secretariat_user.id],
                              [task.responsible for task in tasks])
        self.assertEqual(["Neuer Aufgaben Titel", "Neuer Aufgaben Titel"],
                         [task.title for task in tasks])

    @browsing
    def test_skip_rejected(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.set_workflow_state('task-state-rejected', self.seq_subtask_1)

        url = '{}/@workflow/task-transition-rejected-skipped'.format(
            self.seq_subtask_1.absolute_url())

        data = {'text': u'Ist nicht notwendig.'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'task-state-skipped', api.content.get_state(self.seq_subtask_1))
        self.assertEqual(
            'task-state-open', api.content.get_state(self.seq_subtask_2))

        response = IResponseContainer(self.seq_subtask_1)[-1]
        self.assertEqual(u'Ist nicht notwendig.', response.text)
        self.assertEqual('task-transition-rejected-skipped', response.transition)

    @browsing
    def test_skip_planed_task(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/task-transition-planned-skipped'.format(
            self.seq_subtask_2.absolute_url())

        data = {'text': u'Ist nicht notwendig.'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'task-state-skipped', api.content.get_state(self.seq_subtask_2))
        self.assertEqual(
            'task-state-open', api.content.get_state(self.seq_subtask_3))

        response = IResponseContainer(self.seq_subtask_2)[-1]
        self.assertEqual(u'Ist nicht notwendig.', response.text)
        self.assertEqual('task-transition-planned-skipped', response.transition)
