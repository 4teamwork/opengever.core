from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.base.model import create_session
from opengever.task.adapters import IResponseContainer
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase


class TestTeamTasks(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_select_a_team_as_responsible_is_possible(self, browser):
        self.login(self.regular_user, browser)

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier)
            factoriesmenu.add('Task')
            browser.fill({'Title': u'Team Task', 'Task Type': 'To comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill('team:1')
            browser.find('Save').click()

        task = children.get('added').pop()

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

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier)
            factoriesmenu.add('Task')
            browser.fill({'Title': u'Team Task', 'Task Type': 'To comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill('team:2')
            browser.find('Save').click()
            create_session().flush()

        task = children.get('added').pop()
        center = notification_center()
        # Assign watchers to a local variable in order to avoid having
        # a "stale association proxy" when the GC collects within the
        # list comprehension.
        watchers = center.get_watchers(task)
        self.assertEquals(
            [u'team:2', u'kathi.barfuss'],
            [watcher.actorid for watcher in watchers]
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

    @browsing
    def test_responsible_change_is_visible_in_the_response(self, browser):
        self.login(self.regular_user, browser)

        ITask(self.task).responsible = u'team:1'
        self.task.get_sql_object().responsible = u'team:1'
        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-open-in-progress')
        browser.fill({'Response': u'Das \xfcbernehme ich!'})
        browser.click_on('Save')

        response = IResponseContainer(self.task)[-1]
        expected = [{'before': u'team:1',
                     'after': 'kathi.barfuss',
                     'id': 'responsible',
                     'name': u'label_responsible'}]

        self.assertEqual(
            expected, [dict(change) for change in response.changes])

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEqual(
            u'Accepted by B\xe4rfuss K\xe4thi (kathi.barfuss), responsible '
            u'changed from Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt) to '
            u'B\xe4rfuss K\xe4thi (kathi.barfuss).',
            browser.css('.answer h3').text[0])

    def test_multi_admin_unit_team_task(self):
        self.login(self.regular_user)

        ITask(self.task).responsible = u'team:1'
        self.task.get_sql_object().responsible = u'team:1'
        self.set_workflow_state('task-state-open', self.task)

        successor = accept_task_with_successor(
            self.dossier, self.task.oguid.id, u'Ok.')

        self.assertEquals(self.regular_user.getId(), successor.responsible)
        self.assertEquals(
            self.regular_user.getId(), successor.get_sql_object().responsible)
        self.assertEquals(
            [{'after': 'kathi.barfuss', 'id': 'responsible',
              'name': u'label_responsible', 'before': u'team:1'}],
            IResponseContainer(self.task)[-1].changes)
        self.assertEquals('task-transition-open-in-progress',
                          IResponseContainer(self.task)[-1].transition)

    @browsing
    def test_multi_admin_unit_team_task_edit_in_issuer_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        self.add_additional_admin_and_org_unit()

        ITask(self.task).responsible = u'team:1'
        ITask(self.task).responsible_client = u'gdgs'
        self.task.get_sql_object().responsible = u'team:1'
        self.task.get_sql_object().assigned_org_unit = u'gdgs'

        self.set_workflow_state('task-state-open', self.task)

        browser.open(self.task)
        browser.click_on('task-transition-open-in-progress')
        browser.fill({'Accept the task and ...': 'participate'})
        browser.click_on('Continue')

        self.assertEquals(self.regular_user.getId(), self.task.responsible)
        self.assertEquals(self.regular_user.getId(),
                          self.task.get_sql_object().responsible)
