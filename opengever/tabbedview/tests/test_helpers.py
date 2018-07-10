from datetime import date
from ftw.testing import MockTestCase
from opengever.tabbedview.helper import readable_date
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.helper import tooltip_helper
from opengever.testing import IntegrationTestCase


class TestHelpers(IntegrationTestCase):

    def test_task_id_checkbox_helper(self):
        self.login(self.regular_user)
        sql_task = self.task.get_sql_object()

        self.assertEquals(
            task_id_checkbox_helper(sql_task, ''),
            u'<input class="noborder selectable" id="2" name="task_ids:list" '
            u'title="Select Vertragsentwurf \xdcberpr\xfcfen" type="checkbox" value="2" />')

    def test_readable_date_from_datetime_string(self):
        self.assertEqual(
            readable_date({}, '2017-12-31T11:17:00.137Z'), '31.12.2017')

    def test_readable_date_from_invalid_string(self):
        self.assertEqual(
            readable_date({}, 'foo'), '')

    def test_readable_date_from_date_object(self):
        self.assertEqual(
            readable_date({}, date(2017, 12, 31)), '31.12.2017')

    def test_tooltip_helper_accepts_unicode(self):
        tooltip = tooltip_helper({}, u'B\xe4rengraben')
        self.assertIsInstance(tooltip, str)
        self.assertEqual(
            '<span title="B\xc3\xa4rengraben">B\xc3\xa4rengraben</span>',
            tooltip)

    def test_tooltip_helper_accepts_bytestring(self):
        tooltip = tooltip_helper({}, 'B\xc3\xa4rengraben')
        self.assertIsInstance(tooltip, str)
        self.assertEqual(
            '<span title="B\xc3\xa4rengraben">B\xc3\xa4rengraben</span>',
            tooltip)

    def test_tooltip_helper_deals_with_none(self):
        tooltip = tooltip_helper({}, None)
        self.assertIsInstance(tooltip, str)
        self.assertEqual('<span title=""></span>', tooltip)
