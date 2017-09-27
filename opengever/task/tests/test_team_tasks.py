from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.base.model import create_session
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase


class TestTeamTasks(IntegrationTestCase):

    features = ('activity', )

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

    @browsing
    def test_only_team_members_count_as_responsible(self, browser):
        self.login(self.regular_user, browser)

        ITask(self.task).responsible = u'team:2'
        self.task.get_sql_object().responsible = u'team:2'
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            ['task-transition-reassign', 'label_add_comment'],
            browser.css('.actionButtons li').text,
            'Expect none responsible actions, because the regular_user is not '
            'a team member and therefore not a responsible.')

        self.login(self.meeting_user, browser)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            ['task-transition-open-in-progress',
             'task-transition-open-rejected',
             'task-transition-open-resolved',
             'task-transition-reassign',
             'label_add_comment'],
            browser.css('.actionButtons li').text,
            'Expect responsible actions, because the meeting_user is a team '
            'member and therefore not a responsible.')

    @browsing
    def test_all_team_members_are_notified_for_a_new_team_task(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Task')

        browser.fill({'Title': u'Team Task', 'Task Type': 'To comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:2')
        browser.find('Save').click()
        create_session().flush()

        task = self.dossier.get('task-3')

        center = notification_center()
        self.assertEquals(
            [u'team:2', u'kathi.barfuss'],
            [watcher.actorid for watcher in center.get_watchers(task)]
        )

        activity = Activity.query.one()

        self.assertEquals(
            [u'franzi.muller', u'herbert.jager'],
            [note.userid for note in activity.notifications])

    @browsing
    def test_set_current_user_as_responsible_when_accepting_a_team_task(self, browser):
        self.login(self.regular_user, browser)

        ITask(self.task).responsible = u'team:1'
        self.task.get_sql_object().responsible = u'team:1'
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')

        browser.click_on('task-transition-open-in-progress')
        browser.fill({'Response': u'Das \xfcbernehme ich!'})
        browser.click_on('Save')

        self.assertEquals(self.regular_user.getId(),
                          ITask(self.task).responsible)
        self.assertEquals(self.regular_user.getId(),
                          self.task.get_sql_object().responsible)
