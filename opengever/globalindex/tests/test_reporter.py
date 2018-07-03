from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestTaskReporter(FunctionalTestCase):

    def setUp(self):
        super(TestTaskReporter, self).setUp()
        self.task = create(Builder('task')
                           .titled(u'Export Task')
                           .having(task_type='comment',
                                   deadline=date(2012, 7, 1),)
                           .in_state('task-state-open'))

    @browsing
    def test_task_report(self, browser):
        browser.login().open(view='task_report',
                             data={'task_ids': [self.task.id]})

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        self.assertSequenceEqual(
            [u'Export Task',
             u'task-state-open',
             datetime(2012, 7, 1),
             None,
             None,
             u'Test User (test_user_1_)',
             u'Org Unit 1',
             u'Test User (test_user_1_)',
             u'To comment',
             u'admin-unit-1',
             1L],
            [cell.value for cell in list(workbook.active.rows)[1]])
