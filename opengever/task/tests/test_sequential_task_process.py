from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Resource
from opengever.base.oguid import Oguid
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides


class TestSequentialTaskProcess(IntegrationTestCase):

    features = ('activity', )

    def test_starts_next_task_when_task_gets_resolved(self):
        self.login(self.regular_user)

        # create subtask
        subtask2 = create(Builder('task')
                          .within(self.task)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-planned'))

        self.set_workflow_state('task-state-in-progress', self.subtask)
        alsoProvides(self.subtask, IFromSequentialTasktemplate)
        alsoProvides(subtask2, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

    def test_starts_next_task_when_task_gets_closed(self):
        self.login(self.regular_user)

        # create subtask
        subtask2 = create(Builder('task')
                          .within(self.task)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-planned'))

        self.set_workflow_state('task-state-in-progress', self.subtask)
        alsoProvides(self.subtask, IFromSequentialTasktemplate)
        alsoProvides(subtask2, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask, subtask2])
        self.subtask.task_type = 'direct-execution'
        api.content.transition(
            obj=self.subtask, transition='task-transition-in-progress-tested-and-closed')

        self.assertEquals(
            'task-state-tested-and-closed', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

    def test_starts_next_task_when_open_task_gets_closed(self):
        self.login(self.regular_user)

        self.seq_subtask_1.task_type = 'information'
        self.seq_subtask_1.sync()

        api.content.transition(
            obj=self.seq_subtask_1,
            transition='task-transition-open-tested-and-closed')

        self.assertEquals(
            'task-state-tested-and-closed', api.content.get_state(self.seq_subtask_1))
        self.assertEquals(
            'task-state-open', api.content.get_state(self.seq_subtask_2))

    def test_starts_next_task_when_task_gets_skipped(self):
        self.login(self.dossier_responsible)

        # create subtask
        subtask2 = create(Builder('task')
                          .within(self.task)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-planned'))

        self.set_workflow_state('task-state-planned', self.subtask)
        alsoProvides(self.subtask, IFromSequentialTasktemplate)
        alsoProvides(subtask2, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-planned-skipped')

        self.assertEquals(
            'task-state-skipped', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

        self.set_workflow_state('task-state-rejected', self.subtask)
        self.set_workflow_state('task-state-planned', subtask2)
        api.content.transition(
            obj=self.subtask, transition='task-transition-rejected-skipped')

        self.assertEquals(
            'task-state-skipped', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

    def test_handles_already_opened_tasks(self):
        self.login(self.regular_user)

        # create subtask
        subtask2 = create(Builder('task')
                          .within(self.task)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-open'))

        self.set_workflow_state('task-state-in-progress', self.subtask)
        alsoProvides(self.subtask, IFromSequentialTasktemplate)
        alsoProvides(subtask2, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

    def test_record_activity_when_open_next_task(self):
        self.login(self.regular_user)

        # create subtask
        subtask2 = create(Builder('task')
                          .within(self.task)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-planned'))

        self.set_workflow_state('task-state-in-progress', self.subtask)
        alsoProvides(self.subtask, IFromSequentialTasktemplate)
        alsoProvides(subtask2, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

        activities = Resource.query.get_by_oguid(
            Oguid.for_object(subtask2)).activities
        activity = activities[-1]
        self.assertEquals('task-added', activity.kind)
        self.assertEquals('Task opened', activity.label)
        self.assertEquals(u'New task opened by B\xe4rfuss K\xe4thi',
                          activity.summary)
        self.assertEquals(Oguid.for_object(subtask2), activity.resource.oguid)


class TestInitialStateForSubtasks(IntegrationTestCase):

    @browsing
    def test_is_open_for_regular_subtasks(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.task) as children:
            browser.open(self.task, view='++add++opengever.task.task')
            browser.fill({'Title': 'Subtas', 'Task Type': 'comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(self.secretariat_user)
            browser.click_on('Save')

        subtask = children['added'].pop()
        self.assertEquals('task-state-open', api.content.get_state(subtask))

    @browsing
    def test_is_planned_for_sequence_process_subtasks(self, browser):
        self.login(self.regular_user, browser=browser)
        alsoProvides(self.task, IFromSequentialTasktemplate)
        self.task.set_tasktemplate_order([self.subtask])

        with self.observe_children(self.task) as children:
            browser.open(self.task, view='++add++opengever.task.task')
            browser.fill({'Title': 'Subtas', 'Task Type': 'comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(self.secretariat_user)
            browser.click_on('Save')

        subtask = children['added'].pop()
        self.assertEquals('task-state-planned', api.content.get_state(subtask))


class TestAddingAdditionalTaskToSequentialProcess(IntegrationTestCase):

    @browsing
    def test_position_field_is_not_visible(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.sequential_task,
                     view='++add++opengever.task.task?position=1')

        self.assertIsNone(browser.find_field_by_text('Tasktemplate Position'))

    @browsing
    def test_adds_task_to_the_given_position(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.sequential_task,
                     view='++add++opengever.task.task?position=1')
        browser.fill({'Title': 'Subtask', 'Task Type': 'comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.click_on('Save')

        oguids = self.sequential_task.get_tasktemplate_order()
        self.assertEquals(
            [u'Mitarbeiter Dossier generieren',
             u'Subtask',
             u'Arbeitsplatz vorbereiten',
             u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [oguid.resolve_object().title for oguid in oguids])

    @browsing
    def test_adds_task_to_the_end_if_no_position_is_given(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.sequential_task, view='++add++opengever.task.task')
        browser.fill({'Title': 'Subtask', 'Task Type': 'comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.click_on('Save')

        oguids = self.sequential_task.get_tasktemplate_order()
        self.assertEquals(
            [u'Mitarbeiter Dossier generieren',
             u'Arbeitsplatz vorbereiten',
             u'Vorstellungsrunde bei anderen Mitarbeitern',
             u'Subtask'],
            [oguid.resolve_object().title for oguid in oguids])
