from datetime import datetime
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestTaskReporter(IntegrationTestCase):

    @browsing
    def test_task_report(self, browser):
        self.login(self.regular_user, browser=browser)

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
            [u'label_task_title', u'review_state',
             u'label_deadline', u'label_completed',
             u'label_dossier_title', u'label_issuer',
             u'label_issuing_org_unit', u'label_responsible',
             u'label_task_type', 'label_admin_unit_id', u'label_sequence_number'],
            [cell.value for cell in list(workbook.active.rows)[0]])

        # self.task
        self.assertSequenceEqual(
            [self.task.title,  u'task-state-in-progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.dossier.title, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'For confirmation / correction', u'plone', 1],
            [cell.value for cell in list(workbook.active.rows)[1]])

        # self.meeting_task
        self.assertSequenceEqual(
            [self.meeting_task.title, u'task-state-in-progress',
             datetime(2016, 11, 1, 0, 0), None,
             self.meeting_dossier.title, u'Ziegler Robert (robert.ziegler)',
             u'Finanz\xe4mt', u'Ziegler Robert (robert.ziegler)',
             u'For confirmation / correction', u'plone', 9],
            [cell.value for cell in list(workbook.active.rows)[2]])
