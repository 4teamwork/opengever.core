from ftw.testing import MockTestCase
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.users import linked_value_helper
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


class TestLinkedValueHelper(MockTestCase):

    def test_returns_empty_string_for_none_value(self):
        item = self.stub()
        self.replay()

        self.assertEquals('', linked_value_helper(item, None))

    def test_returns_username_linked_to_profile(self):
        item = self.stub()
        self.expect(item.userid).result('hugo.boss')

        info = self.stub()
        self.mock_utility(info, IContactInformation)
        self.expect(info.get_profile_url('hugo.boss')).result(
            'http://localhost:8080/userdetails/hugo-boss')

        self.replay()

        self.assertEquals(
            '<a href="http://localhost:8080/userdetails/hugo-boss">Hugo</a>',
            linked_value_helper(item, 'Hugo'))

    def test_returns_only_value_for_values_without_a_entry_in_ogds(self):
        item = self.stub()
        self.expect(item.userid).result('hugo.boss')

        info = self.stub()
        self.mock_utility(info, IContactInformation)
        self.expect(info.get_profile_url('hugo.boss')).result(None)

        self.replay()

        self.assertEquals('Hugo', linked_value_helper(item, 'Hugo'))
