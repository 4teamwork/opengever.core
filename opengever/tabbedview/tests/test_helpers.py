from ftw.testing import MockTestCase
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.helper import linked_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper


class TestDocumentsUrl(MockTestCase):

    def test_task_id_checkbox_helper(self):

        brain = self.stub()
        self.expect(brain.title).result('The brain of a task')
        self.expect(brain.task_id).result('123')

        self.replay()

        self.assertEquals(
            task_id_checkbox_helper(brain, ''),
            '<input class="noborder selectable" id="123" name="task_ids:list" '
            'title="Select The brain of a task" type="checkbox" value="123" />')
