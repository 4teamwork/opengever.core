from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.base.interfaces import ISequenceNumber
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from zope.component import getUtility


class TestToDoList(IntegrationTestCase):

    @browsing
    def test_todolist_is_addable_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        browser.visit(self.workspace)
        factoriesmenu.add('ToDo list')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Retrospektive'})
        form.save()

        assert_no_error_messages(browser)

        todolist = browser.context
        self.assertEqual('todolist-3', todolist.id)
        self.assertEqual('Retrospektive', todolist.title)

    @browsing
    def test_todos_are_addable_in_a_todolist(self, browser):
        self.login(self.workspace_member, browser)

        browser.visit(self.todolist_general)
        factoriesmenu.add('ToDo')

        form = browser.find_form_by_field('Title')
        form.fill({'Title': u'Bitte Vorbereitungen treffen.'})
        form.save()

        assert_no_error_messages(browser)
        todo, = self.todolist_general.objectValues()
        self.assertEqual(u'Bitte Vorbereitungen treffen.', todo.title)

    def test_todolist_is_searchable_by_title(self):
        self.login(self.workspace_member)
        self.assertItemsEqual(
            ['allgemeine', 'informationen'],
            index_data_for(self.todolist_general).get('SearchableText'))

    def test_todolist_uses_a_global_and_separate_sequencenumber_counter(self):
        self.login(self.workspace_member)
        sequence = getUtility(ISequenceNumber)

        self.assertEqual(1, sequence.get_number(self.todolist_general))
        self.assertEqual(2, sequence.get_number(self.todolist_introduction))

        todolist = create(Builder('todolist').titled(u'Konzeptphase'))
        self.assertEqual(3, sequence.get_number(todolist))

    def test_todolist_id_is_todolist_dash_and_sequence_number(self):
        self.login(self.workspace_member)

        self.assertEqual('todolist-1', self.todolist_general.id)
        self.assertEqual('todolist-2', self.todolist_introduction.id)

        todolist = create(Builder('todolist').titled(u'Konzeptphase'))
        self.assertEqual('todolist-3', todolist.id)
