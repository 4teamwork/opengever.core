from datetime import date
from ftw.testing import MockTestCase
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.helper import readable_date


class TestHelpers(MockTestCase):

    def test_task_id_checkbox_helper(self):

        brain = self.stub()
        self.expect(brain.title).result('The brain of a task')
        self.expect(brain.task_id).result('123')

        self.replay()

        self.assertEquals(
            task_id_checkbox_helper(brain, ''),
            '<input class="noborder selectable" id="123" name="task_ids:list" '
            'title="Select The brain of a task" type="checkbox" value="123" />')

    def test_readable_date_from_datetime_string(self):
        self.assertEqual(
            readable_date({}, '2017-12-31T11:17:00.137Z'), '31.12.2017')

    def test_readable_date_from_invalid_string(self):
        self.assertEqual(
            readable_date({}, 'foo'), '')

    def test_readable_date_from_date_object(self):
        self.assertEqual(
            readable_date({}, date(2017, 12, 31)), '31.12.2017')
