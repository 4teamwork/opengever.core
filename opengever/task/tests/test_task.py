from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.dexterity import erroneous_fields
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.activity.model import Activity
from opengever.base.response import IResponseContainer
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from opengever.task.task_response import TaskResponse
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from z3c.relationfield.relation import RelationValue
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds


class TestTaskSolrIntegration(SolrIntegrationTestCase):

    features = ('solr', 'activity')

    def test_adding(self):
        self.login(self.regular_user)
        t1 = create(
            Builder("task")
            .within(self.dossier)
            .titled("Task 1")
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
            )
        )
        self.assertTrue(ITask.providedBy(t1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        schema = fti.lookupSchema()
        self.assertEqual(ITask, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(ITask.providedBy(new_object))

    def test_view(self):
        self.login(self.regular_user)

        view = self.subtask.restrictedTraverse('@@tabbedview_view-overview')
        self.assertEqual([], view.get_sub_tasks())

        view = self.task.restrictedTraverse('@@tabbedview_view-overview')
        self.assertEqual([self.subtask.get_sql_object()], view.get_sub_tasks())

    @browsing
    def test_task_title_length_is_validated_to_a_max_of_256(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, view='++add++opengever.task.task')

        browser.fill({'Title': 257 * 'x',
                      'Task type': 'To comment',
                      })

        org_unit = get_current_org_unit()

        # Fill Responible manually
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            org_unit.id() + ':' + self.regular_user.getId())
        browser.find('Save').click()

        self.assertEqual({u'Title': ['Value is too long']},
                         erroneous_fields())

        browser.fill({'Title': 256 * 'x'})

        # We need to fill it again, because of a known bug in lxml
        # https://github.com/4teamwork/ftw.testbrowser/pull/17
        # https://github.com/4teamwork/ftw.testbrowser/issues/53
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            org_unit.id() + ':' + self.regular_user.getId())

        browser.find('Save').click()
        self.assertTrue(len(self.dossier.objectValues()),
                        'Expect one item in dossier')

    def test_relateddocuments(self):
        self.login(self.dossier_responsible)

        # self.document is related to self.task
        # self.taskdocument is contained in self.task

        view = self.task.restrictedTraverse('tabbedview_view-relateddocuments')
        results = [aa.Title for aa in view.table_source.search_results(
            view.table_source.build_query())]
        self.assertTrue(self.document.Title() in results)

        # check sorting
        view.request.set('sort', u'sortable_title')
        results = [aa.Title for aa in view.table_source.search_results(
            view.table_source.build_query())]
        self.assertTrue(results == [self.taskdocument.Title(), self.document.Title()])

        view.request.set('ACTUAL_URL', self.task.absolute_url())
        self.assertTrue(view())

    def test_documents_returns_related_documents_and_containing_documents(self):
        self.login(self.regular_user)

        intids = getUtility(IIntIds)
        ITask(self.task).relatedItems = [
            RelationValue(intids.getId(self.document))]

        self.assertIn(self.taskdocument, self.task.listFolderContents())
        self.assertItemsEqual([self.taskdocument, self.document], self.task.task_documents())

    def test_addresponse(self):
        self.login(self.dossier_responsible)

        res = TaskResponse("")
        container = IResponseContainer(self.task)
        container.add(res)
        self.assertTrue(res in container)

    @browsing
    def test_addresponse_fails_without_transition(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.task, view='addresponse')

    def test_task_type_category(self):
        self.login(self.dossier_responsible)

        self.task.task_type = u'information'
        self.assertEqual(
            u'unidirectional_by_reference', self.task.task_type_category)
        self.task.task_type = u'approval'
        self.assertEqual(
            u'bidirectional_by_reference', self.task.task_type_category)

    @browsing
    def test_task_with_invalid_unicode_character_in_text_is_displayed(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        task = self.task.get_sql_object()
        task.text = u'\uf04aHello Unicode Error Character!'

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertIn('Hello Unicode Error Character!', browser.contents)

    def test_task_date_subscriber(self):
        self.login(self.dossier_responsible)

        task = create(
            Builder("task")
            .within(self.dossier)
            .titled("Task 1")
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=u'fa',
            )
            .in_state('task-state-open')
        )

        wft = self.portal.portal_workflow

        self.assertEqual(task.expectedStartOfWork, None)
        wft.doActionFor(task, 'task-transition-open-in-progress')

        self.assertEqual(task.expectedStartOfWork, date.today())

        self.assertEqual(task.date_of_completion, None)
        wft.doActionFor(task, 'task-transition-in-progress-resolved')
        self.assertEqual(task.date_of_completion, date.today())

        wft.doActionFor(task, 'task-transition-resolved-in-progress')
        self.assertEqual(task.date_of_completion, None)

        task = create(
            Builder("task")
            .within(self.dossier)
            .titled("Task 2")
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=u'fa',
            )
            .in_state('task-state-open')
        )

        self.assertEqual(task.date_of_completion, None)
        self.login(self.administrator)
        wft.doActionFor(task, 'task-transition-open-tested-and-closed')
        self.assertEqual(task.date_of_completion, date.today())

    def test_adding_a_subtask_adds_a_response_on_main_task(self):
        self.login(self.dossier_responsible)

        intids = getUtility(IIntIds)
        subtask = create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=u'fa',
            )
        )

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual(intids.getId(subtask), response.added_objects[0].to_id)
        self.assertEqual('transition-add-subtask', response.transition)

    def test_adding_a_subtask_via_remote_request_does_not_add_response_to_main_task(self):
        self.login(self.dossier_responsible)

        responses = len(IResponseContainer(self.task))

        # all different remote requests should not
        # generate an response
        self.request.environ['HTTP_X_OGDS_AC'] = 'token'
        create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=u'fa',
            )
        )
        self.assertEqual(responses, len(IResponseContainer(self.task)))

        del self.request.environ['HTTP_X_OGDS_AC']
        self.request.set('X-CREATING-SUCCESSOR', True)
        create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=u'fa',
            )
        )
        self.assertEqual(responses, len(IResponseContainer(self.task)))

    def test_adding_a_document_adds_response_on_main_task(self):
        self.login(self.dossier_responsible)

        intids = getUtility(IIntIds)
        document = create(
            Builder('document')
            .within(self.task)
            .titled('Letter to Peter')
        )

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual(intids.getId(document), response.added_objects[0].to_id)
        self.assertEqual('transition-add-document', response.transition)

    def test_closing_an_open_subtask_adds_response_on_parent_task(self):
        self.login(self.regular_user)
        subtask = create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
                task_type=u'information',
            )
        )

        api.content.transition(obj=subtask,
                               transition='task-transition-open-tested-and-closed')

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual('transition-close-subtask', response.transition)
        self.assertEqual(response.subtask.to_object, subtask)

    def test_closing_an_in_progress_subtask_adds_response_on_parent_task(self):
        self.login(self.regular_user)
        subtask = create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
                task_type=u'direct-execution',
            )
            .in_progress()
        )

        api.content.transition(obj=subtask,
                               transition='task-transition-in-progress-tested-and-closed')

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual('transition-close-subtask', response.transition)
        self.assertEqual(response.subtask.to_object, subtask)

    def test_closing_a_resolved_subtask_adds_response_on_parent_task(self):
        self.login(self.dossier_responsible)
        api.content.transition(obj=self.subtask,
                               transition='task-transition-resolved-tested-and-closed')

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual('transition-close-subtask', response.transition)
        self.assertEqual(response.subtask.to_object, self.subtask)

    def test_cancelling_an_open_subtask_adds_response_on_parent_task(self):
        self.login(self.dossier_responsible)
        subtask = create(
            Builder("task")
            .within(self.task)
            .titled("Subtask")
            .having(
                issuer=self.dossier_responsible.getId(),
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
                task_type=u'information',
            )
        )

        api.content.transition(obj=subtask,
                               transition='task-transition-open-cancelled')

        response = IResponseContainer(self.task).list()[-1]
        self.assertEqual('transition-cancel-subtask', response.transition)
        self.assertEqual(response.subtask.to_object, subtask)

    @browsing
    def test_responsible_client_for_multiple_orgunits(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.visit(self.dossier)
        factoriesmenu.add('Task')

        browser.fill({'Title': 'Task title',
                      'Task type': 'To comment'})
        form = browser.find_form_by_field('Responsible')
        org_unit = get_current_org_unit()
        form.find_widget('Responsible').fill(
            org_unit.id() + ':' + self.dossier_responsible.getId())
        browser.find('Save').click()

        task = self.dossier.objectValues()[-1]
        self.assertEqual(
            org_unit.id(),
            task.responsible_client,
            'The client should be stored after submitting the form')
        self.assertEqual(
            self.dossier_responsible.getId(),
            task.responsible,
            'The user should be stored after submitting the form')

    @browsing
    def test_cannot_set_responsible_client_for_disabled_orgunit(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        org_unit = get_current_org_unit()
        org_unit.enabled = False

        browser.open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Task title',
                      'Task type': 'To comment'})

        # Fill responsible manually
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            org_unit.id() + ':' + self.dossier_responsible.getId())
        browser.find('Save').click()

        self.assertEqual(['There were some errors.'], error_messages())
        self.assertEqual(
            ['Required input is missing.'],
            browser.css('#formfield-form-widgets-responsible_client .error').text)

    @browsing
    def test_cannot_set_responsible_client_for_hidden_orgunit(self, browser):
        """Responsibles from a hidden orgunit are valid, but the widget does
        not allow us to choose them. We therefore need to test searching the
        responsible directly in the widget.
        """
        self.login(self.dossier_responsible, browser=browser)

        org_unit = get_current_org_unit()

        widget_url = "{}/{}".format(
            self.dossier.absolute_url(),
            '++add++opengever.task.task/++widget++form.widgets.responsible')
        search_url = widget_url + '/search?q={}:{}'.format(
            org_unit.id(), self.dossier_responsible.getId())

        search_result = browser.open(search_url).json
        self.assertEqual(1, search_result['total_count'])

        org_unit.hidden = True
        search_result = browser.open(search_url).json
        self.assertEqual(0, search_result['total_count'])

    @browsing
    def test_create_a_task_for_every_selected_person_with_multiple_orgunits(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        org_unit = get_current_org_unit()
        responsible_users = [
            org_unit.id() + ':' + self.dossier_responsible.getId(),
            'rk' + ':' + self.foreign_contributor.getId(),
        ]

        browser.visit(self.empty_dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Task title',
                      'Task type': 'To comment',
                      'Related items': self.document})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible_users)

        browser.find('Save').click()
        tasks = filter(lambda item: ITask.providedBy(item),
                       self.empty_dossier.objectValues())
        self.assertEqual(2, len(tasks), 'Expect 2 tasks')
        self.assertEqual(self.dossier_responsible.getId(), tasks[0].responsible)
        self.assertEqual(org_unit.id(), tasks[0].responsible_client)
        self.assertEqual(self.foreign_contributor.getId(), tasks[1].responsible)
        self.assertEqual('rk', tasks[1].responsible_client)

        activities = Activity.query.all()
        self.assertEqual(2, len(activities))
        self.assertEqual(u'task-added', activities[0].kind)
        self.assertEqual(self.dossier_responsible.getId(), activities[0].actor_id)
        self.assertEqual(u'task-added', activities[1].kind)
        self.assertEqual(self.dossier_responsible.getId(), activities[1].actor_id)

    @browsing
    def test_create_a_task_for_every_selected_person_with_one_orgunit(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        org_unit = get_current_org_unit()
        responsible_users = [
            org_unit.id() + ':' + self.dossier_responsible.getId(),
            org_unit.id() + ':' + self.regular_user.getId(),
        ]

        browser.visit(self.empty_dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Task title',
                      'Task type': 'To comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible_users)

        browser.find('Save').click()

        tasks = self.empty_dossier.objectValues()
        self.assertEqual(2, len(tasks), 'Expect 2 tasks')
        self.assertEqual(self.dossier_responsible.getId(), tasks[0].responsible)
        self.assertEqual(org_unit.id(), tasks[0].responsible_client)
        self.assertEqual(self.regular_user.getId(), tasks[1].responsible)
        self.assertEqual(org_unit.id(), tasks[1].responsible_client)

        activities = Activity.query.all()
        self.assertEqual(2, len(activities))
        self.assertEqual(u'task-added', activities[0].kind)
        self.assertEqual(self.dossier_responsible.getId(), activities[0].actor_id)
        self.assertEqual(u'task-added', activities[1].kind)
        self.assertEqual(self.dossier_responsible.getId(), activities[1].actor_id)


class TestTaskIntegration(IntegrationTestCase):

    def test_is_open(self):
        self.login(self.regular_user)
        # open
        self.assertTrue(self.seq_subtask_1.is_open())
        # in progress
        self.assertFalse(self.task.is_open())
        # resolved
        self.assertFalse(self.subtask.is_open())

    def test_is_pending(self):
        self.login(self.regular_user)
        # open
        self.assertTrue(self.seq_subtask_1.is_pending())
        # in progress
        self.assertTrue(self.task.is_pending())
        # resolved
        self.assertTrue(self.subtask.is_pending())

        wft = self.portal.portal_workflow
        wft.doActionFor(self.seq_subtask_1, 'task-transition-open-tested-and-closed')
        self.assertFalse(self.seq_subtask_1.is_pending())

    def test_is_in_final_state(self):
        self.login(self.regular_user)
        # in progress
        self.assertFalse(self.task.is_in_final_state)
        # resolved
        self.assertFalse(self.subtask.is_in_final_state)

        # closed
        wft = self.portal.portal_workflow
        wft.doActionFor(self.seq_subtask_1, 'task-transition-open-tested-and-closed')
        self.assertTrue(self.seq_subtask_1.is_in_final_state)


class TestDossierSequenceNumber(IntegrationTestCase):

    def test_if_task_is_inside_a_maindossier_is_maindossier_number(self):
        self.login(self.dossier_responsible)

        task = create(
            Builder('task')
            .within(self.dossier)
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
            ))

        self.assertEqual(
            self.dossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_if_task_is_inside_a_subdossier_is_subdossiers_number(self):
        self.login(self.dossier_responsible)

        task = create(
            Builder('task')
            .within(self.subdossier)
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
            ))

        self.assertEqual(
            self.subdossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_handles_multiple_levels_of_subdossier_correctly(self):
        self.login(self.dossier_responsible)

        task = create(
            Builder('task')
            .within(self.subsubdossier)
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
            ))

        self.assertEqual(
            self.subsubdossier.get_sequence_number(),
            task.get_dossier_sequence_number())

    def test_its_inboxs_number_for_forwardings(self):
        self.login(self.secretariat_user)

        task = create(
            Builder('task')
            .within(self.inbox)
            .having(
                responsible=self.regular_user.getId(),
                responsible_client=u'fa',
            ))

        self.assertEqual(None, task.get_dossier_sequence_number())


class TestDeadlineDefaultValue(IntegrationTestCase):

    @browsing
    def test_deadline_is_today_plus_five_working_days_by_default(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        today = datetime(2023, 3, 6)  # Monday

        with freeze(today):
            browser.open(self.empty_dossier, view='++add++opengever.task.task')

        browser.fill({'Title': 'Test task',
                      'Task type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            get_current_org_unit().id() + ':' + self.dossier_responsible.getId())

        browser.css('#form-buttons-save').first.click()

        # Monday in one week (Monday + 5 days excluding weekends)
        expected = today + timedelta(days=7)
        self.assertEqual(expected.date(), self.empty_dossier.objectValues()[0].deadline)

    @browsing
    def test_deadline_use_registry_entry_to_calculate_timedelta(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        today = datetime(2023, 3, 6)  # Monday

        registry = getUtility(IRegistry)
        registry.forInterface(ITaskSettings).deadline_timedelta = 3

        with freeze(today):
            browser.open(self.empty_dossier, view='++add++opengever.task.task')

        browser.fill({'Title': 'Test task',
                      'Task type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            get_current_org_unit().id() + ':' + self.dossier_responsible.getId())

        browser.css('#form-buttons-save').first.click()

        expected = today + timedelta(days=3)
        self.assertEqual(expected.date(), self.empty_dossier.objectValues()[0].deadline)

    @browsing
    def test_task_text_is_xss_safe(self, browser):

        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.empty_dossier, view='++add++opengever.task.task')

        task_text = '<p>text comes here</p><img src="http://not.found/" onerror="script:alert(\'XSS\');" />'
        browser.fill({'Title': 'Test task',
                      'Task type': 'comment',
                      'Text': task_text})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            get_current_org_unit().id() + ':' + self.dossier_responsible.getId())

        browser.css('#form-buttons-save').first.click()

        task_text_output = self.empty_dossier.objectValues()[0].text.output
        expected_task_text = '<p>text comes here</p><img src="http://not.found/" />'
        self.assertNotIn('onerror="script:alert(\'XSS\');"', task_text_output)
        self.assertIn(expected_task_text, task_text_output)


class TestTaskTypeTranslations(IntegrationTestCase):

    @browsing
    def test_task_types_are_translated(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.addSupportedLanguage('de-ch')
        lang_tool.setDefaultLanguage('de-ch')

        browser.open(self.dossier, view='++add++opengever.task.task')
        task_type_widget = browser.forms['form'].find_widget('Auftragstyp')
        task_type_labels = task_type_widget.inputs_by_label.keys()
        self.assertEqual([
            'Zur Genehmigung',
            'Zur Stellungnahme',
            u'Zur Pr\xfcfung / Korrektur',
            'Zur direkten Erledigung',
            'Zum Bericht / Antrag',
            'Zur Kenntnisnahme'],
            task_type_labels)


class TestForceCloseTask(IntegrationTestCase):

    @browsing
    def test_force_update_open_main_task_without_subtasks(self, browser):
        self.login(self.dossier_responsible)
        dossier = create(Builder('dossier'))
        task = create(
            Builder('task')
            .within(dossier)
            .in_state('task-state-open')
            .titled('Main task')
            .having(
                issuer=self.dossier_responsible.getId(),
                responsible=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        self.assertEqual('task-state-open', api.content.get_state(task))
        task.close_task()
        self.assertEqual('task-state-cancelled', api.content.get_state(task))

    @browsing
    def test_force_update_in_progress_main_task_without_subtasks(self, browser):
        self.login(self.dossier_responsible)
        dossier = create(Builder('dossier'))
        task = create(
            Builder('task')
            .within(dossier)
            .in_state('task-state-in-progress')
            .titled('Main task')
            .having(
                issuer=self.dossier_responsible.getId(),
                responsible=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        self.assertEqual('task-state-in-progress', api.content.get_state(task))
        task.close_task()
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(task))

    @browsing
    def test_force_update_resolved_main_task_without_subtasks(self, browser):
        self.login(self.dossier_responsible)
        dossier = create(Builder('dossier'))
        task = create(
            Builder('task')
            .within(dossier)
            .in_state('task-state-resolved')
            .titled('Main task')
            .having(
                issuer=self.dossier_responsible.getId(),
                responsible=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        self.assertEqual('task-state-resolved', api.content.get_state(task))
        task.close_task()
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(task))

    @browsing
    def test_close_task_open_with_subtask(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier'))
        main_task = create(
            Builder("task")
            .within(dossier)
            .in_state('task-state-open')
            .titled("Main Task")
            .having(
                responsible=self.dossier_responsible.getId(),
                issuer=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        subtask1 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-resolved')
            .titled("Subtask 1")
            .having(task_type='correction',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask2 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-in-progress')
            .titled("Subtask 2")
            .having(task_type='information',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask3 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-open')
            .titled("Subtask 3")
            .having(task_type='approval',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask4 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-rejected')
            .titled("Subtask 4")
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )

        main_task.close_task()

        # If the main task is cancelled, every subtask will be cancelled as well
        self.assertEqual('task-state-cancelled', api.content.get_state(main_task))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask1))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask2))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask3))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask4))

    @browsing
    def test_close_task_in_progress_with_subtask(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier'))
        main_task = create(
            Builder("task")
            .within(dossier)
            .in_state('task-state-in-progress')
            .titled("Main Task")
            .having(
                responsible=self.dossier_responsible.getId(),
                issuer=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        subtask1 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-resolved')
            .titled("Subtask 1")
            .having(task_type='correction',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask2 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-in-progress')
            .titled("Subtask 2")
            .having(task_type='information',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask3 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-open')
            .titled("Subtask 3")
            .having(task_type='approval',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask4 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-rejected')
            .titled("Subtask 4")
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )

        main_task.close_task()

        self.assertEqual('task-state-tested-and-closed', api.content.get_state(main_task))
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(subtask1))
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(subtask2))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask3))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask4))

    @browsing
    def test_close_task_resolved_with_subtask(self, browser):
        self.login(self.dossier_responsible, browser)

        dossier = create(Builder('dossier'))
        main_task = create(
            Builder("task")
            .within(dossier)
            .in_state('task-state-resolved')
            .titled("Main Task")
            .having(
                responsible=self.dossier_responsible.getId(),
                issuer=self.dossier_responsible.getId(),
                responsible_client='fa',
                task_type='information'
            )
        )

        subtask1 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-resolved')
            .titled("Subtask 1")
            .having(task_type='correction',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask2 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-in-progress')
            .titled("Subtask 2")
            .having(task_type='information',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask3 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-open')
            .titled("Subtask 3")
            .having(task_type='approval',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        subtask4 = create(
            Builder("task")
            .within(main_task)
            .in_state('task-state-rejected')
            .titled("Subtask 4")
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )

        main_task.close_task()

        self.assertEqual('task-state-tested-and-closed', api.content.get_state(main_task))
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(subtask1))
        self.assertEqual('task-state-tested-and-closed', api.content.get_state(subtask2))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask3))
        self.assertEqual('task-state-cancelled', api.content.get_state(subtask4))

    @browsing
    def test_close_task_variations(self, browser):
        self.login(self.dossier_responsible, browser)

        # Task type information
        task_information_open = create(
            Builder("task")
            .within(self.dossier)
            .titled("Subtask 1")
            .in_state('task-state-open')
            .having(task_type='information',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_information_open.close_task()

        task_information_in_progress = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-in-progress')
            .titled("Subtask 2")
            .having(task_type='information',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_information_in_progress.close_task()

        # Task type approval
        task_approval_open = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-open')
            .titled("Subtask 3")
            .having(task_type='approval',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_approval_open.close_task()

        task_approval_in_progress = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-in-progress')
            .titled("Subtask 3")
            .having(task_type='approval',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_approval_in_progress.close_task()

        task_approval_resolved = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-resolved')
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_approval_resolved.close_task()

        # Task type direct execution
        task_direct_execution_open = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-open')
            .titled("Subtask 5")
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_direct_execution_open.close_task()

        task_direct_execution_in_progress = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-in-progress')
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_direct_execution_in_progress.close_task()

        task_direct_execution_rejected = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-rejected')
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_direct_execution_rejected.close_task()

        task_direct_execution_resolved = create(
            Builder("task")
            .within(self.dossier)
            .in_state('task-state-resolved')
            .having(task_type='direct-execution',
                    issuer=self.dossier_responsible.getId(),
                    responsible=self.dossier_responsible.getId(),
                    responsible_client='fa')
        )
        task_direct_execution_resolved.close_task()

        self.assertDictEqual(
            {
                'task_information_open': 'task-state-cancelled',
                'task_information_in_progress': 'task-state-tested-and-closed',

                'task_approval_open': 'task-state-cancelled',
                'task_approval_in_progress': 'task-state-tested-and-closed',
                'task_approval_resolved': 'task-state-tested-and-closed',

                'task_direct_execution_open': 'task-state-cancelled',
                'task_direct_execution_in_progress': 'task-state-tested-and-closed',
                'task_direct_execution_rejected': 'task-state-cancelled',
                'task_direct_execution_resolved': 'task-state-tested-and-closed',
            },
            {
                'task_information_open': api.content.get_state(task_information_open),
                'task_information_in_progress': api.content.get_state(task_information_in_progress),
                'task_approval_open': api.content.get_state(task_approval_open),
                'task_approval_in_progress': api.content.get_state(task_approval_in_progress),
                'task_approval_resolved': api.content.get_state(task_approval_resolved),
                'task_direct_execution_open': api.content.get_state(task_direct_execution_open),
                'task_direct_execution_in_progress': api.content.get_state(task_direct_execution_in_progress),
                'task_direct_execution_rejected': api.content.get_state(task_direct_execution_rejected),
                'task_direct_execution_resolved': api.content.get_state(task_direct_execution_resolved),
            },
        )
