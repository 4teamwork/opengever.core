from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.todo import ACTIVE_TODO_STATE
from opengever.workspace.todo import COMPLETED_TODO_STATE


class TestToggleTodos(IntegrationTestCase):

    @browsing
    def test_toggle_todo_will_toggle_the_review_state_and_is_completed_property(self, browser):
        self.login(self.workspace_member, browser)

        response = browser.open(
            self.todo, view="@toggle", method='POST',
            headers={'Accept': 'application/json'}).json

        self.assertEqual(200, browser.status_code)
        self.assertTrue(response.get(u'is_completed'))
        self.assertEqual(COMPLETED_TODO_STATE, response.get(u'review_state'))

        response = browser.open(
            self.todo, view="@toggle", method='POST',
            headers={'Accept': 'application/json'}).json

        self.assertEqual(200, browser.status_code)
        self.assertFalse(response.get(u'is_completed'))
        self.assertEqual(ACTIVE_TODO_STATE, response.get(u'review_state'))
