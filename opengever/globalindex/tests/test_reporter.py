from datetime import datetime
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
import json


class TestTaskReporter(IntegrationTestCase):

    @browsing
    def test_task_report(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method='PATCH', headers=self.api_headers,
                     data=json.dumps({'text': 'A description'}))

        browser.open(view='task_report',
                     data={'view_name': 'mytasks',
                           'task_ids': [self.task.get_sql_object().task_id,
                                        self.meeting_task.get_sql_object().task_id,
                                        self.subtask.get_sql_object().task_id]})

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        # labels
        self.assertSequenceEqual(
            [u'Title', u'State',
             u'Deadline', u'Completed on',
             u'Dossier', u'Main task', u'Issuer',
             u'Issuing organization', u'Responsible',
             u'Task type', 'Tenant', u'Sequence number',
             u'Description'],
            [cell.value for cell in list(workbook.active.rows)[0]])

        # self.task
        self.assertSequenceEqual(
            [self.task.title,  u'In progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.dossier.title, None, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'For your review', u'plone', 1, u'A description'],
            [cell.value for cell in list(workbook.active.rows)[1]])

        # self.meeting_task
        self.assertSequenceEqual(
            [self.meeting_task.title, u'In progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.meeting_dossier.title, None, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'Ziegler Robert (robert.ziegler)',
             u'For your review', u'plone', 9, None],
            [cell.value for cell in list(workbook.active.rows)[2]])

        # self.subtask
        self.assertSequenceEqual(
            [self.subtask.title,  u'Resolved',
             datetime(2016, 11, 1, 0, 0), None,
             self.dossier.title, self.task.title, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'For your review', u'plone', 2, None],
            [cell.value for cell in list(workbook.active.rows)[3]])

    @browsing
    def test_respects_column_tabbedview_settings_if_exists(self, browser):
        self.login(self.regular_user, browser=browser)

        # Changing tabbedviews grid state (order and visible columns)
        data = {'view_name': 'mytasks',
                'gridstate': json.dumps({
                    u'sort': {u'field': u'modified', u'direction': u'ASC'},
                    u'columns': [
                        {u'width': 30, u'id': u'task_id_checkbox_helper'},
                        {u'width': 110, u'sortable': True, u'id': u'sequence_number'},
                        {u'width': 110, u'sortable': True, u'id': u'review_state'},
                        {u'width': 110, u'sortable': True, u'id': u'responsible'},
                        {u'width': 110, u'sortable': True, u'id': u'issuer'},
                        {u'width': 110, u'sortable': True, u'id': u'task_type'},
                        {u'width': 110, u'sortable': True, u'id': u'title'},
                        {u'width': 110, u'hidden': True, u'sortable': True, u'id': u'deadline'},
                        {u'width': 110, u'hidden': True, u'sortable': True, u'id': u'completed'},
                        {u'width': 110, u'hidden': True, u'sortable': True, u'id': u'created'},
                        {u'width': 110, u'sortable': True, u'id': u'containing_dossier'},
                        {u'width': 110, u'sortable': True, u'id': u'issuing_org_unit'},
                        {u'width': 1, u'hidden': True, u'id': u'dummy'}]})}

        browser.open(view='@@tabbed_view/setgridstate', data=data)

        browser.open(view='task_report',
                     data={'view_name': 'mytasks',
                           'task_ids': [self.task.get_sql_object().task_id,
                                        self.meeting_task.get_sql_object().task_id]})

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        # labels
        self.assertSequenceEqual(
            [u'Sequence number', u'State',
             u'Responsible', u'Issuer',
             u'Task type', u'Title',
             u'Dossier'],
            [cell.value for cell in list(workbook.active.rows)[0]])

    @browsing
    def test_task_report_by_task_ressource_id(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='task_report',
                     data={'view_name': 'mytasks',
                           'tasks': [self.task.absolute_url(),
                                     self.meeting_task.absolute_url()]})

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        # self.task
        task_cells = list(workbook.active.rows)[1]
        self.assertSequenceEqual(
            [self.task.title,  u'In progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.dossier.title, None, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'For your review', u'plone', 1, None],
            [cell.value for cell in task_cells])
        self.assertEqual(self.task.absolute_url(), task_cells[0].hyperlink.target)

        # self.meeting_task
        self.assertSequenceEqual(
            [self.meeting_task.title, u'In progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.meeting_dossier.title, None, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'Ziegler Robert (robert.ziegler)',
             u'For your review', u'plone', 9, None],
            [cell.value for cell in list(workbook.active.rows)[2]])
