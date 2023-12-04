from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.api.task import SerializeTaskResponseToJson
from opengever.base.response import IResponseContainer
from opengever.document.approvals import APPROVED_IN_CURRENT_VERSION
from opengever.document.approvals import IApprovalList
from opengever.ogds.models.user import User
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from operator import attrgetter
from plone import api
from plone.uuid.interfaces import IUUID
from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.globalrequest import getRequest
import json


class TestAPISupport(IntegrationTestCase):

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

        self.assertEqual([self.regular_user.id, self.secretariat_user.id],
                         [watcher.actorid for watcher in watchers])


class TestAPITransitions(IntegrationTestCase):

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

        response = IResponseContainer(self.seq_subtask_1).list()[-1]

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

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual(
            [{'after': date(2019, 11, 23),
              'field_id': 'deadline',
              'field_title': u'label_deadline',
              'before': date(2016, 11, 1)}],
            response.changes)

    @browsing
    def test_modify_deadline_with_same_deadline_as_before_raises_an_error(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@workflow/task-transition-modify-deadline'.format(
            self.task.absolute_url())

        data = {'new_deadline': self.task.deadline.strftime('%Y-%m-%d')}

        with browser.expect_http_error(400):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(
            u'The entered deadline is the same as the current one.',
            browser.json['additional_metadata']["fields"][0]['translated_message'])

        self.assertIn(
            'same_deadline_error',
            browser.json.get('message'))

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

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.subtask).list()[-1]
        self.assertEqual(u'Done!', response.text)
        self.assertEqual('task-transition-open-tested-and-closed',
                         response.transition)

    @browsing
    def test_resolve_successful(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-in-progress-resolved'.format(self.subtask.absolute_url())

        data = {'text': 'Erledigt, siehe Anhang.',
                'relatedItems': [self.mail_eml.absolute_url()]}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-resolved',
                         api.content.get_state(self.subtask))

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.task).list()[-1]
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

        org_unit = self.add_additional_admin_and_org_unit()[1]
        create(Builder('ogds_user')
               .id('johny.english')
               .having(firstname=u'Johnny', lastname=u'English')
               .assign_to_org_units([org_unit]))

        url = '{}/@workflow/task-transition-reassign'.format(
            self.task.absolute_url())
        data = {'text': 'Robert macht das.',
                'responsible': 'johnny.english',
                'responsible_client': u'gdgs'}

        with browser.expect_http_error(400):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

    @browsing
    def test_reassign_only_unit_changes(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_workflow_state('task-state-open', self.task)

        # Add regular user to gdgs orgunit
        org_unit = self.add_additional_admin_and_org_unit()[1]
        ogds_user = User.query.get(self.regular_user.id)
        org_unit.users_group.users.append(ogds_user)

        url = '{}/@workflow/task-transition-reassign'.format(self.task.absolute_url())
        data = {'text': 'Robert macht das.',
                'responsible': self.regular_user.id,
                'responsible_client': u'gdgs'}
        browser.open(url, method='POST', data=json.dumps(data), headers=self.api_headers)

        self.assertEqual('gdgs', self.task.responsible_client)
        self.assertEqual(self.regular_user.id, self.task.responsible)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEqual(
            u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to B\xe4rfuss K\xe4thi (kathi.barfuss)',
            browser.css('.answers h3')[0].text)

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

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.subtask).list()[-1]
        self.assertEqual(u'Kann nicht.', response.text)
        self.assertEqual('task-transition-open-rejected', response.transition)
        self.assertEqual([{'after': self.dossier_responsible.id,
                           'field_id': 'responsible',
                           'field_title': u'label_responsible',
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

        response = IResponseContainer(self.subtask).list()[-1]
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

        response = IResponseContainer(self.subtask).list()[-1]
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
    def test_delegate_a_task_notifies_informed_principals(self, browser):
        self.activate_feature('activity')
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-delegate'.format(
            self.subtask.absolute_url())

        data = {"title": "Neuer Aufgaben Titel",
                "responsibles": ["fa:{}".format(self.meeting_user.id)],
                "issuer": self.dossier_responsible.id,
                "informed_principals": [self.administrator.id, self.archivist.id],
                "deadline": "2018-12-03"}

        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        activity = Activity.query.one()
        self.assertEqual('task-added', activity.kind)
        self.assertEqual(4, len(activity.notifications))
        self.assertItemsEqual([
            self.administrator.id,
            self.archivist.id,
            self.dossier_responsible.id,
            self.meeting_user.id],
          [notification.userid for notification in activity.notifications])

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

        response = IResponseContainer(self.seq_subtask_1).list()[-1]
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
            'task-state-planned', api.content.get_state(self.seq_subtask_3))

        response = IResponseContainer(self.seq_subtask_2).list()[-1]
        self.assertEqual(u'Ist nicht notwendig.', response.text)
        self.assertEqual('task-transition-planned-skipped', response.transition)

    @browsing
    def test_reopen_a_skipped_task_successfull(self, browser):
        self.login(self.secretariat_user, browser=browser)

        self.set_workflow_state('task-state-skipped', self.seq_subtask_2)

        url = '{}/@workflow/task-transition-skipped-open'.format(
            self.seq_subtask_2.absolute_url())
        data = {'text': u'Muss trotzdem gemacht werden.'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'task-state-open', api.content.get_state(self.seq_subtask_2))
        self.assertEqual(
            'task-state-open', self.seq_subtask_2.get_sql_object().review_state)

        response = IResponseContainer(self.seq_subtask_2).list()[-1]
        self.assertEqual(u'Muss trotzdem gemacht werden.', response.text)
        self.assertEqual('task-transition-skipped-open', response.transition)


class TestApprovalViaTask(IntegrationTestCase):

    def create_task_for_approval(self, browser, with_docs=True):
        self.login(self.dossier_responsible, browser=browser)
        task = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='fa',
                    task_type='approval'))

        if with_docs:
            # Also freeze time here so that task responses are ordered correctly
            with freeze(datetime(2021, 8, 18, 12, 30)):
                contained_doc = create(
                    Builder('document')
                    .within(task)
                    .titled(u'Vertr\xe4gsentwurf'))

                intids = getUtility(IIntIds)
                related_doc = self.document
                relation = RelationValue(intids.getId(related_doc))
                ITask(task).relatedItems.append(relation)

        self.set_workflow_state('task-state-in-progress', task)
        if with_docs:
            return task, contained_doc, related_doc
        else:
            return task

    @browsing
    def test_approve_docs_on_resolve(self, browser):
        task, contained_doc, related_doc = self.create_task_for_approval(browser)
        self.login(self.regular_user, browser=browser)

        url = '{}/@workflow/task-transition-in-progress-resolved'.format(task.absolute_url())

        data = {'text': 'Sind alle genehmigt',
                'approved_documents': [
                    IUUID(contained_doc), IUUID(related_doc)]}

        with freeze(datetime(2021, 8, 18, 12, 45)):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('task-state-resolved',
                         api.content.get_state(task))

        self.assertEqual([{
            'approver': self.regular_user.id,
            'task_uid': IUUID(task),
            'approved': datetime(2021, 8, 18, 12, 45),
            'version_id': 0}],
            IApprovalList(contained_doc).storage.list())

        self.assertEqual([{
            'approver': self.regular_user.id,
            'task_uid': IUUID(task),
            'approved': datetime(2021, 8, 18, 12, 45),
            'version_id': 0}],
            IApprovalList(related_doc).storage.list())

        response = IResponseContainer(task).list()[-1]
        self.assertEqual('task-transition-in-progress-resolved',
                         response.transition)

        # Task response should contain references to approved documents
        approved_docs = map(attrgetter('to_object'), response.approved_documents)
        self.assertItemsEqual([contained_doc, related_doc], approved_docs)

        serializer = SerializeTaskResponseToJson(response, getRequest())
        serialized = serializer(container=task)

        self.assertEqual(2, len(serialized['approved_documents']))
        expected_approved_docs = [
            {u'@id': contained_doc.absolute_url(),
             u'@type': u'opengever.document.document',
             u'UID': contained_doc.UID(),
             u'checked_out': None,
             u'description': u'',
             u'file_extension': u'',
             u'is_leafnode': None,
             u'review_state': u'document-state-draft',
             u'title': u'Vertr\xe4gsentwurf'},
            {u'@id': related_doc.absolute_url(),
             u'@type': u'opengever.document.document',
             u'UID': related_doc.UID(),
             u'checked_out': None,
             u'description': u'Wichtige Vertr\xe4ge',
             u'file_extension': u'.docx',
             u'is_leafnode': None,
             u'review_state': u'document-state-draft',
             u'title': u'Vertr\xe4gsentwurf'},
        ]
        self.assertItemsEqual(expected_approved_docs,
                              serialized['approved_documents'])

    @browsing
    def test_approve_docs_on_resolve_rejects_docs_not_associated_with_task(self, browser):
        task = self.create_task_for_approval(
            browser, with_docs=False)
        self.login(self.regular_user, browser=browser)

        url = '{}/@workflow/task-transition-in-progress-resolved'.format(task.absolute_url())

        data = {'text': 'Dieses Dokument ist gar nicht in der Aufgabe',
                'approved_documents': [IUUID(self.proposaldocument)]}

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual('task-state-in-progress', api.content.get_state(task))
        self.assertEqual([], IApprovalList(self.proposaldocument).storage.list())

    @browsing
    def test_can_only_approve_docs_for_tasks_of_type_approval(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.subtask)

        url = '{}/@workflow/task-transition-in-progress-resolved'.format(
            self.subtask.absolute_url())

        data = {'text': 'Diese Aufgabe ist gar nicht zur Genehmigung',
                'approved_documents': [IUUID(self.document)]}

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual({
            u'message': u"Param 'approved_documents' is only supported "
                        u"for tasks of task_type 'approval'.",
            u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_closed_to_open_successfully(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.task)

        url = '{}/@workflow/task-transition-tested-and-closed-in-progress'.format(
            self.task.absolute_url())

        data = {'text': 'Falsche Aktion'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'task-state-in-progress', api.content.get_state(self.task))
        self.assertEqual(
            'task-state-in-progress', self.task.get_sql_object().review_state)

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual('Falsche Aktion', response.text)
        self.assertEqual('task-transition-tested-and-closed-in-progress', response.transition)
