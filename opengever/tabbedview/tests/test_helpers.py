from ftw.testing import MockTestCase
from mocker import ANY
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.helper import linked_ogds_author
from opengever.tabbedview.helper import task_id_checkbox_helper
from opengever.tabbedview.utils import get_containg_document_tab_url
from zope.interface import Interface


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
