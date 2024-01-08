from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.activity.model import Resource
from opengever.base.oguid import Oguid
from opengever.journal.tests.utils import get_journal_entry
from opengever.journal.tests.utils import get_journal_length
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from opengever.testing import IntegrationTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from urlparse import urlparse
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
        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)
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
        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)
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

    def test_open_next_task_skips_skipped_tasks(self):
        self.login(self.regular_user)

        self.set_workflow_state('task-state-in-progress', self.seq_subtask_1)
        self.set_workflow_state('task-state-skipped', self.seq_subtask_2)

        api.content.transition(
            obj=self.seq_subtask_1,
            transition='task-transition-in-progress-tested-and-closed')

        self.assertEquals('task-state-skipped',
                          api.content.get_state(self.seq_subtask_2))
        self.assertEquals('task-state-open',
                          api.content.get_state(self.seq_subtask_3))

    def test_starts_next_task_when_rejected_task_gets_skipped(self):
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
        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)

        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-planned-skipped')

        # Skipping a planned task - does not open the next task
        self.assertEquals(
            'task-state-skipped', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-planned', api.content.get_state(subtask2))

        self.set_workflow_state('task-state-rejected', self.subtask)
        self.set_workflow_state('task-state-planned', subtask2)
        api.content.transition(
            obj=self.subtask, transition='task-transition-rejected-skipped')

        self.assertEquals(
            'task-state-skipped', api.content.get_state(self.subtask))

        # Skipping a rejected task - does not open the next task
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
        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        api.content.transition(
            obj=self.subtask, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-open', api.content.get_state(subtask2))

    def test_does_not_allow_to_manually_start_sequential_task_if_parent_not_in_progress(self):
        self.login(self.regular_user)

        subsubtask = create(Builder('task')
                            .within(self.subtask)
                            .having(responsible_client='fa',
                                    responsible=self.regular_user.getId(),
                                    issuer=self.dossier_responsible.getId(),
                                    task_type='correction',
                                    deadline=date(2016, 11, 1))
                            .in_state('task-state-planned'))

        self.set_workflow_state('task-state-planned', self.subtask)
        alsoProvides(self.task, IContainParallelProcess)
        alsoProvides(self.subtask, IContainSequentialProcess)
        alsoProvides(subsubtask, IPartOfSequentialProcess)
        self.subtask.set_tasktemplate_order([subsubtask])

        with self.assertRaises(InvalidParameterError):
            api.content.transition(
                obj=subsubtask, transition='task-transition-planned-open')

    def test_handles_missing_permissions_on_next_task(self):
        self.login(self.regular_user)

        # create subtasks
        subtask1 = create(Builder('task')
                          .within(self.task_in_protected_dossier)
                          .having(responsible_client='fa',
                                  responsible=self.regular_user.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-open'))

        subtask2 = create(Builder('task')
                          .within(self.task_in_protected_dossier)
                          .having(responsible_client='fa',
                                  responsible=self.dossier_responsible.getId(),
                                  issuer=self.dossier_responsible.getId(),
                                  task_type='correction',
                                  deadline=date(2016, 11, 1))
                          .in_state('task-state-planned'))

        alsoProvides(self.task_in_protected_dossier, IContainSequentialProcess)
        alsoProvides(subtask1, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)

        self.task_in_protected_dossier.set_tasktemplate_order([subtask1, subtask2])

        api.content.transition(
            obj=subtask1, transition='task-transition-open-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(subtask1))
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

        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)

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

    @browsing
    def test_automatically_opened_task_has_icon_and_message_in_history(self, browser):
        self.login(self.regular_user, browser=browser)

        # The second subtask is in the state "planned" by default. This fact is useful for
        # understanding the purpose of this test. It's not something we "need" to test.
        # Its state will change when the first subtask is completed (later on in this test).
        self.assertEquals(
            'task-state-planned',
            api.content.get_state(self.seq_subtask_2)
        )

        # Complete the first subtask. This will trigger a state change
        # of the second subtask. This is just for the understanding of this test.
        browser.open(self.seq_subtask_1)
        browser.click_on('Accept')
        browser.click_on('Save')
        browser.click_on('Close')
        browser.click_on('Save')

        # The state of the second subtask has changed. No we can assert some things.
        self.assertEquals(
            'task-state-open',
            api.content.get_state(self.seq_subtask_2)
        )
        browser.open(self.seq_subtask_2, view='tabbedview_view-overview')

        # The response history has two items, one for the initial "planned" and
        # one for the "open" state. We're only interested in the "open" state.
        answer = browser.css('.answer').first

        # The answer now has a class "open". This was not the case until now and
        # this is what we are fixing in this pull request.
        self.assertEquals(
            'answer open',
            answer.attrib['class']
        )

        # The answer also features a message. This was not the case until now and
        # this is what we are fixing in this pull request.
        self.assertEquals(
            [u'Task opened by B\xe4rfuss K\xe4thi (kathi.barfuss)'],
            answer.css('h3').text
        )

    @browsing
    def test_can_manually_start_first_task_when_necessary(self, browser):
        self.login(self.regular_user, browser)

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

        alsoProvides(self.task, IContainSequentialProcess)
        alsoProvides(self.subtask, IPartOfSequentialProcess)
        alsoProvides(subtask2, IPartOfSequentialProcess)
        self.task.set_tasktemplate_order([self.subtask, subtask2])

        wftool = api.portal.get_tool("portal_workflow")
        actions = wftool.listActionInfos(object=self.subtask)
        available_transitions = [action['id'] for action in actions
                                 if action['category'] == 'workflow']
        self.assertIn('task-transition-planned-open', available_transitions)

        browser.open(self.subtask)
        browser.click_on("Start")
        browser.click_on("Save")

        self.assertEquals(
            'task-state-open', api.content.get_state(self.subtask))

    def test_starts_parallel_subprocess(self):
        self.login(self.secretariat_user)

        # make seq_subtask_2 a parallel subprocess
        alsoProvides(self.seq_subtask_2, IContainParallelProcess)
        subprocess_task1 = create(Builder('task')
                                  .within(self.seq_subtask_2)
                                  .having(responsible_client='fa',
                                          responsible=self.regular_user.getId(),
                                          issuer=self.dossier_responsible.getId(),
                                          task_type='correction')
                                  .in_state('task-state-planned'))
        subprocess_task2 = create(Builder('task')
                                  .within(self.seq_subtask_2)
                                  .having(responsible_client='fa',
                                          responsible=self.regular_user.getId(),
                                          issuer=self.dossier_responsible.getId(),
                                          task_type='correction')
                                  .in_state('task-state-planned'))
        alsoProvides(subprocess_task2, IContainParallelProcess)
        subprocess_task2_task1 = create(Builder('task')
                                        .within(subprocess_task2)
                                        .having(responsible_client='fa',
                                                responsible=self.regular_user.getId(),
                                                issuer=self.dossier_responsible.getId(),
                                                task_type='correction')
                                        .in_state('task-state-planned'))

        # Add a document to verify that all started subtasks also have
        # relations to the doc if 'pass_documents_to_next_task' is set.
        doc = create(Builder('document').within(self.seq_subtask_1))

        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.doActionFor(
            self.seq_subtask_1,
            'task-transition-open-tested-and-closed',
            transition_params={
                'pass_documents_to_next_task': True,
            }
        )

        self.assertEquals(
            'task-state-open', api.content.get_state(subprocess_task1))
        self.assertEquals(doc, subprocess_task1.relatedItems[0].to_object)

        self.assertEquals(
            'task-state-open', api.content.get_state(subprocess_task2))
        self.assertEquals(doc, subprocess_task2.relatedItems[0].to_object)

        self.assertEquals(
            'task-state-open', api.content.get_state(subprocess_task2_task1))
        self.assertEquals(doc, subprocess_task2_task1.relatedItems[0].to_object)

    def test_starts_sequential_subprocess(self):
        self.login(self.secretariat_user)

        # make seq_subtask_2 a sequential subprocess
        alsoProvides(self.seq_subtask_2, IContainSequentialProcess)
        subprocess_task1 = create(Builder('task')
                                  .within(self.seq_subtask_2)
                                  .having(responsible_client='fa',
                                          responsible=self.regular_user.getId(),
                                          issuer=self.dossier_responsible.getId(),
                                          task_type='correction')
                                  .in_state('task-state-planned'))

        alsoProvides(subprocess_task1, IContainSequentialProcess)
        subprocess_task1_task1 = create(Builder('task')
                                        .within(subprocess_task1)
                                        .having(responsible_client='fa',
                                                responsible=self.regular_user.getId(),
                                                issuer=self.dossier_responsible.getId(),
                                                task_type='correction')
                                        .in_state('task-state-planned'))

        subprocess_task2 = create(Builder('task')
                                  .within(self.seq_subtask_2)
                                  .having(responsible_client='fa',
                                          responsible=self.regular_user.getId(),
                                          issuer=self.dossier_responsible.getId(),
                                          task_type='correction')
                                  .in_state('task-state-planned'))

        self.seq_subtask_2.set_tasktemplate_order([subprocess_task1, subprocess_task2])

        # Add a document to verify that all started subtasks also have
        # relations to the doc if 'pass_documents_to_next_task' is set.
        doc = create(Builder('document').within(self.seq_subtask_1))

        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.doActionFor(
            self.seq_subtask_1,
            'task-transition-open-tested-and-closed',
            transition_params={
                'pass_documents_to_next_task': True,
            }
        )

        self.assertEquals(
            'task-state-open', api.content.get_state(subprocess_task1))
        self.assertEquals(doc, subprocess_task1.relatedItems[0].to_object)

        self.assertEquals(
            'task-state-open', api.content.get_state(subprocess_task1_task1))
        self.assertEquals(doc, subprocess_task1_task1.relatedItems[0].to_object)

        self.assertEquals(
            'task-state-planned', api.content.get_state(subprocess_task2))
        self.assertEquals(0, len(subprocess_task2.relatedItems))


class TestInitialStateForSubtasks(IntegrationTestCase):

    @browsing
    def test_is_open_for_regular_subtasks(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.task) as children:
            browser.open(self.task, view='++add++opengever.task.task')
            browser.fill({'Title': 'Subtas', 'Task type': 'comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(self.secretariat_user)
            browser.click_on('Save')

        subtask = children['added'].pop()
        self.assertEquals('task-state-open', api.content.get_state(subtask))

    @browsing
    def test_is_planned_for_sequence_process_subtasks(self, browser):
        self.login(self.regular_user, browser=browser)
        alsoProvides(self.task, IContainSequentialProcess)
        self.task.set_tasktemplate_order([self.subtask])

        with self.observe_children(self.task) as children:
            browser.open(self.task, view='++add++opengever.task.task')
            browser.fill({'Title': 'Subtas', 'Task type': 'comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(self.secretariat_user)
            browser.click_on('Save')

        subtask = children['added'].pop()
        self.assertEquals('task-state-planned', api.content.get_state(subtask))


class TestAddingAdditionalTaskToSequentialProcess(IntegrationTestCase):

    @browsing
    def test_add_previous_task_buttons_is_only_visible_if_next_task_is_not_yet_started(self, browser):
        self.login(self.regular_user, browser=browser)

        # First task is already started - so position 0 button is not available
        browser.open(self.sequential_task, view='tabbedview_view-overview')
        self.assertEquals(
            ['position=1', 'position=2', ''],
            [urlparse(link.get('href')).query for link in browser.css('.add-task')])

        # Second task is also started - so position 0 and 1 button aren't available
        self.set_workflow_state('task-state-tested-and-closed', self.seq_subtask_1)
        self.set_workflow_state('task-state-open', self.seq_subtask_2)
        browser.open(self.sequential_task, view='tabbedview_view-overview')
        self.assertEquals(
            ['position=2', ''],
            [urlparse(link.get('href')).query for link in browser.css('.add-task')])

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
        browser.fill({'Title': 'Subtask', 'Task type': 'comment'})
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
    def test_added_task_is_part_of_sequence(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.sequential_task) as subtasks:
            browser.open(self.sequential_task,
                         view='++add++opengever.task.task?position=1')
            browser.fill({'Title': 'Subtask', 'Task type': 'comment'})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(self.secretariat_user)
            browser.click_on('Save')

        additional_task, = subtasks['added']
        self.assertTrue(IPartOfSequentialProcess.providedBy(additional_task))

        self.assertEquals(
            additional_task.get_sql_object(),
            self.seq_subtask_1.get_sql_object().tasktemplate_successor)

    @browsing
    def test_adds_task_to_the_end_if_no_position_is_given(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.sequential_task, view='++add++opengever.task.task')
        browser.fill({'Title': 'Subtask', 'Task type': 'comment'})
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

    @browsing
    def test_zero_position_is_handled_correctly(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.sequential_task, view='++add++opengever.task.task?position=0')
        browser.fill({'Title': 'Subtask', 'Task type': 'comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.click_on('Save')

        oguids = self.sequential_task.get_tasktemplate_order()
        self.assertEquals(
            [u'Subtask',
             u'Mitarbeiter Dossier generieren',
             u'Arbeitsplatz vorbereiten',
             u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [oguid.resolve_object().title for oguid in oguids])


class TestAddingSubtaskToSequentialSubtask(IntegrationTestCase):

    @browsing
    def test_subsubtask_is_not_part_of_sequential_process(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-in-progress', self.seq_subtask_1)

        # Add a subtask
        browser.open(self.seq_subtask_1)
        factoriesmenu.add('Subtask')
        browser.fill({'Title': 'Vertiefte Recherche',
                      'Task type': 'For direct execution'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.regular_user)
        browser.click_on('Save')

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(1, len(self.seq_subtask_1.objectValues()))

        subsubtask = self.seq_subtask_1.objectValues()[0]
        self.assertFalse(subsubtask.is_part_of_sequential_process)
        self.assertIsNone(self.seq_subtask_1.get_tasktemplate_order())


class TestCloseTaskFromTemplate(IntegrationTestCase):

    def test_closes_main_task_if_all_subtasks_are_in_final_state(self):
        self.login(self.administrator)
        self.seq_subtask_1.task_type = 'correction'

        self.assertEquals(
            'task-state-in-progress', api.content.get_state(self.sequential_task))

        api.content.transition(
            obj=self.seq_subtask_2, transition='task-transition-planned-skipped')

        self.assertEquals(
            'task-state-in-progress', api.content.get_state(self.sequential_task))

        api.content.transition(
            obj=self.seq_subtask_1, transition='task-transition-open-resolved')

        self.assertEquals(
            'task-state-in-progress', api.content.get_state(self.sequential_task))

        api.content.transition(
            obj=self.seq_subtask_3, transition='task-transition-open-tested-and-closed')

        self.assertEquals(
            'task-state-in-progress', api.content.get_state(self.sequential_task))

        api.content.transition(
            obj=self.seq_subtask_1, transition='task-transition-resolved-tested-and-closed')

        self.assertEquals(
            'task-state-tested-and-closed', api.content.get_state(self.sequential_task))

    def test_closes_parallel_main_task(self):
        self.login(self.dossier_responsible)
        parallel_task = create(Builder('task')
                               .within(self.dossier)
                               .having(responsible_client='fa',
                                       responsible=self.regular_user.getId(),
                                       issuer=self.dossier_responsible.getId(),
                                       task_type='direct-execution')
                               .in_state('task-state-in-progress')
                               .as_parallel_task())

        parallel_subtask_1 = create(Builder('task')
                                    .within(parallel_task)
                                    .having(responsible_client='fa',
                                            responsible=self.regular_user.getId(),
                                            issuer=self.dossier_responsible.getId(),
                                            task_type='direct-execution')
                                    .in_state('task-state-open')
                                    .as_parallel_task())

        parallel_subtask_2 = create(Builder('task')
                                    .within(parallel_task)
                                    .having(responsible_client='fa',
                                            responsible=self.regular_user.getId(),
                                            issuer=self.dossier_responsible.getId(),
                                            task_type='direct-execution')
                                    .in_state('task-state-open')
                                    .as_parallel_task())

        api.content.transition(
            obj=parallel_subtask_2, transition='task-transition-open-tested-and-closed')

        self.assertEquals(
            'task-state-in-progress', api.content.get_state(parallel_task))

        api.content.transition(
            obj=parallel_subtask_1, transition='task-transition-open-tested-and-closed')

        self.assertEquals(
            'task-state-tested-and-closed', api.content.get_state(parallel_task))

    def test_records_activity_and_adds_journal_entry_when_main_task_is_closed(self):
        self.activate_feature('activity')
        self.login(self.administrator)

        api.content.transition(
            obj=self.seq_subtask_1, transition='task-transition-open-tested-and-closed')

        api.content.transition(
            obj=self.seq_subtask_2, transition='task-transition-open-tested-and-closed')
        length_before_closing_tasks = get_journal_length(self.dossier)

        api.content.transition(
            obj=self.seq_subtask_3, transition='task-transition-open-tested-and-closed')

        activities = Resource.query.get_by_oguid(
            Oguid.for_object(self.sequential_task)).activities

        activity = activities[-1]
        self.assertEqual(u'task-transition-in-progress-tested-and-closed', activity.kind)
        self.assertEqual(u'Task closed', activity.label)

        # Two new entries, one for closing the subtask and one for closing the main task
        self.assertEqual(length_before_closing_tasks + 2, get_journal_length(self.dossier))

        last_journal_entry = get_journal_entry(self.dossier, -1)
        self.assertEqual(last_journal_entry['action']['type'], 'Task modified')
        self.assertEqual(last_journal_entry['actor'], self.administrator.getId())

    def test_close_main_task_is_skipped_if_main_task_is_already_closed(self):
        self.login(self.administrator)
        self.set_workflow_state(
            'task-state-tested-and-closed', self.seq_subtask_1)
        self.set_workflow_state(
            'task-state-tested-and-closed', self.seq_subtask_2)
        self.set_workflow_state(
            'task-state-tested-and-closed', self.sequential_task)
        self.set_workflow_state('task-state-open', self.seq_subtask_3)

        api.content.transition(
            obj=self.seq_subtask_3,
            transition='task-transition-open-tested-and-closed')
