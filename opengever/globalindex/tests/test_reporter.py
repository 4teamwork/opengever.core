from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
import xlrd


class TestTaskReporter(FunctionalTestCase):

    def setUp(self):
        super(TestTaskReporter, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())
        self.task = create(Builder('task')
                           .titled(u'Export Task')
                           .having(task_type='comment',
                                   deadline=date(2012, 7, 1),)
                           .in_state('task-state-open'))

    @browsing
    def test_task_report(self, browser):
        browser.login().open(view='task_report',
                             data={'task_ids': [self.task.id]})
        workbook = xlrd.open_workbook(file_contents=browser.contents)
        sheet = workbook.sheets()[0]
        self.assertSequenceEqual(
            [u'Export Task',
             u'task-state-open',
             u'01.07.2012',
             '',
             '',
             u'Test User (test_user_1_)',
             u'Test User (test_user_1_)',
             u'To comment',
             u'client1',
             u'1'],
            sheet.row_values(1))
