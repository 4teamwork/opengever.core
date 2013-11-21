from ftw.testing import MockTestCase
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.users import linked_value_helper
from opengever.tabbedview.helper import linked_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper


class TestDocumentsUrl(MockTestCase):

    def test_linked_ogds_author(self):

        # mocked links
        HUGOBOSS = '<a href="http://plone/author/hugo.boss">Hugo Boss</a>'
        HANSPETER = '<a href="http://plone/author/hans.peter">Hans Peter</a>'

        brain = self.stub()

        info = self.stub()
        self.mock_utility(info, IContactInformation)

        self.expect(info.is_user('hugo.boss')).result(True)
        self.expect(info.render_link('hugo.boss')).result(HUGOBOSS)

        self.expect(info.is_user(u'hans.peter')).result(False)
        self.expect(info.is_contact(u'hans.peter')).result(True)
        self.expect(info.render_link(u'hans.peter')).result(HANSPETER)

        self.expect(info.is_user('james.bond')).result(False)
        self.expect(info.is_contact('james.bond')).result(False)
        self.expect(info.is_inbox('james.bond')).result(False)

        self.replay()
        self.assertEquals(linked_ogds_author(brain, u'hugo.boss'), HUGOBOSS)
        self.assertEquals(linked_ogds_author(brain, 'hans.peter'), HANSPETER)
        self.assertEquals(
            linked_ogds_author(brain, u'james.bond'), 'james.bond')
        self.assertEquals(linked_ogds_author(brain, None), '')

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
