from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


class TestTeamTasks(IntegrationTestCase):

    @browsing
    def test_select_a_team_as_responsible_is_possible(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier)
        factoriesmenu.add('Task')

        browser.fill({'Title': u'Team Task', 'Task Type': 'To comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:1')
        browser.find('Save').click()

        task = self.dossier.get('task-3')

        self.assertEquals('Team Task', task.title)
        self.assertEquals('team:1', task.responsible)
        self.assertEquals(u'fa', task.responsible_client)
