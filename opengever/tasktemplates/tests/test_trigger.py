from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.dexterity import erroneous_fields
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.tasktemplates import INTERACTIVE_USERS
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import IntegrationTestCase
from plone import api
from requests_toolbelt.utils import formdata


class TestTriggeringTaskTemplate(IntegrationTestCase):

    def trigger_tasktemplatefolder(
            self, browser, folder=u'Verfahren Neuanstellung',
            templates=None, documents=None, start_immediately=None):

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': folder})
        if documents:
            browser.fill({'Related documents': documents})
        browser.click_on('Continue')

        if templates:
            browser.fill({'Tasktemplates': templates})

        if start_immediately is not None:
            browser.fill({'Start immediately': start_immediately})

        browser.click_on('Continue')
        browser.click_on('Trigger')

    @browsing
    def test_redirects_back_and_show_statusmessage_when_no_active_tasktemplatefolder_exists(self, browser):

        self.login(self.regular_user, browser=browser)

        self.set_workflow_state(
            'tasktemplatefolder-state-inactiv', self.tasktemplatefolder)

        browser.open(self.dossier, view='add-tasktemplate')
        self.assertEquals(self.dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['Currently there are no active task template folders registered.'],
            error_messages())

    @browsing
    def test_all_active_tasktemplates_are_listed(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('tasktemplatefolder')
               .titled(u'Einsprache abarbeiten'))
        create(Builder('tasktemplatefolder')
               .titled(u'Einb\xfcrgerungsverfahren')
               .in_state('tasktemplatefolder-state-activ'))

        browser.open(self.dossier, view='add-tasktemplate')

        self.assertEquals(
            [u'Einb\xfcrgerungsverfahren', 'Verfahren Neuanstellung'],
            browser.css('#formfield-form-widgets-tasktemplatefolder').first.options)

    @browsing
    def test_step2_list_all_tasktemplates_of_the_selected_folder_and_preselects_them_correctly(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        create(Builder('tasktemplate')
               .titled(u'User Accounts erstellen.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=False)
        .within(self.tasktemplatefolder))

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': 'Verfahren Neuanstellung'})
        browser.click_on('Continue')

        self.assertItemsEqual(
            ['Notebook einrichten.', 'User Accounts erstellen.',
             'Arbeitsplatz einrichten.'],
            browser.css('#formfield-form-widgets-tasktemplates .option').text)

        self.assertItemsEqual(
            ['Notebook einrichten.'],
            browser.css('#formfield-form-widgets-tasktemplates input[checked]').getparents().text)

    @browsing
    def test_selecting_at_least_one_tasktemplate_is_required(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': 'Verfahren Neuanstellung'})
        browser.click_on('Continue')

        browser.fill({'Tasktemplates': []})
        browser.click_on('Continue')

        self.assertEquals(
            '{}/select-tasktemplates'.format(self.dossier.absolute_url()),
            browser.url)
        self.assertEquals(
            ['Required input is missing.'],
            browser.css('.fieldErrorBox .error').text)

    @browsing
    def test_creates_main_task_assigned_to_current_user(self, browser):
        self.login(self.regular_user, browser=browser)
        self.trigger_tasktemplatefolder(
            browser, templates=[u'Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertEquals(u'Verfahren Neuanstellung', main_task.title)
        self.assertEquals(self.regular_user.getId(), main_task.responsible)
        self.assertEquals(self.regular_user.getId(), main_task.issuer)
        self.assertEquals('direct-execution', main_task.task_type)

    @browsing
    def test_sets_main_task_to_in_progress_state(self, browser):
        self.login(self.regular_user, browser=browser)
        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))

    @browsing
    def test_main_task_deadline_is_the_highest_template_deadline_plus_five(self, browser):
        self.login(self.regular_user, browser=browser)
        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertEquals(
            date.today() + timedelta(days=10 + 5), main_task.deadline)

    @browsing
    def test_all_tasks_are_marked_with_marker_interface(self, browser):
        self.login(self.regular_user, browser=browser)

        # parallel
        self.tasktemplatefolder.sequence_type = u'parallel'
        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertTrue(IFromParallelTasktemplate.providedBy(main_task))
        for subtask in main_task.listFolderContents():
            self.assertTrue(IFromParallelTasktemplate.providedBy(subtask))

        # sequential
        self.tasktemplatefolder.sequence_type = u'sequential'
        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertTrue(IFromSequentialTasktemplate.providedBy(main_task))
        for subtask in main_task.listFolderContents():
            self.assertTrue(IFromSequentialTasktemplate.providedBy(subtask))

    @browsing
    def test_creates_a_subtask_for_each_selected_template(self, browser):
        self.login(self.regular_user, browser=browser)
        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
        .within(self.tasktemplatefolder))

        create(Builder('tasktemplate')
               .titled(u'User Accounts erstellen.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=False)
        .within(self.tasktemplatefolder))

        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.',
                                u'User Accounts erstellen.'])

        main_task = self.dossier.listFolderContents()[-1]
        self.assertEquals(2, len(main_task.listFolderContents()))

        self.assertItemsEqual(
            [u'Arbeitsplatz einrichten.', u'User Accounts erstellen.'],
            [item.title for item in main_task.listFolderContents()])

    @browsing
    def test_step3_shows_responsible_field_for_each_selected_templates(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('tasktemplate')
               .titled(u'Eintrittsgespr\xe4ch vorbereiten und planen.')
               .having(issuer='responsible', responsible_client='fa',
                       responsible='inbox:fa', deadline=10, preselected=True)
               .within(self.tasktemplatefolder))
        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible', deadline=10, preselected=True)
               .within(self.tasktemplatefolder))
        create(Builder('tasktemplate')
               .titled(u'User Accounts erstellen.')
               .having(issuer='responsible', responsible=None,
                       responsible_client=None, deadline=10, preselected=True)
               .within(self.tasktemplatefolder))

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': u'Verfahren Neuanstellung'})
        browser.click_on('Continue')
        browser.fill({'Tasktemplates': [u'Eintrittsgespr\xe4ch vorbereiten und planen.',
                                        'User Accounts erstellen.',
                                        'Arbeitsplatz einrichten.']})
        browser.click_on('Continue')

        # labels
        self.assertItemsEqual(
            [u'Responsible \xabEintrittsgespr\xe4ch vorbereiten und planen.\xbb',
             u'Responsible \xabUser Accounts erstellen.\xbb',
             u'Responsible \xabArbeitsplatz einrichten.\xbb'],
            browser.forms['form'].css('label').text)

        # Default values
        fields = browser.css('select')
        self.assertItemsEqual(
            ['inbox:fa', 'fa:robert.ziegler', None],
            [field.value for field in fields])

        field_name = u'Responsible \xabUser Accounts erstellen.\xbb'
        form = browser.find_form_by_field(field_name)
        form.find_widget(field_name).fill('fa:jurgen.konig')
        browser.click_on('Trigger')

        self.assertEquals(['tasks created'], info_messages())
        main_task = self.dossier.listFolderContents()[-1]
        ids = main_task.objectIds()
        task1, task2, task3 = [main_task.get(_id) for _id in ids]

        self.assertEquals(u'Eintrittsgespr\xe4ch vorbereiten und planen.', task2.title)
        self.assertEquals(u'inbox:fa', task2.responsible)

        self.assertEquals(u'Arbeitsplatz einrichten.', task1.title)
        self.assertEquals(u'robert.ziegler', task1.responsible)

        self.assertEquals(u'User Accounts erstellen.', task3.title)
        self.assertEquals(u'jurgen.konig', task3.responsible)

    @browsing
    def test_step3_responsible_fields_are_required(self, browser):
        self.login(self.regular_user, browser=browser)

        self.tasktemplate.responsible = None
        self.tasktemplate.responsible_client = None

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': u'Verfahren Neuanstellung'})
        browser.click_on('Continue')
        browser.fill({'Tasktemplates': ['Arbeitsplatz einrichten.']})
        browser.click_on('Continue')

        browser.click_on('Trigger')

        self.assertEquals(
            '{}/select-responsibles'.format(self.dossier.absolute_url()),
            browser.url)

        self.assertEquals(
            {u'Responsible \xabArbeitsplatz einrichten.\xbb': ['Required input is missing.']},
            erroneous_fields())

    @browsing
    def test_step3_interactive_responsibles_are_already_resolved(self, browser):
        self.login(self.regular_user, browser=browser)

        self.tasktemplate.responsible = 'responsible'
        self.tasktemplate.responsible_client = INTERACTIVE_USERS

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': u'Verfahren Neuanstellung'})
        browser.click_on('Continue')
        browser.fill({'Tasktemplates': ['Arbeitsplatz einrichten.']})
        browser.click_on('Continue')

        fields =  browser.forms['form'].fields
        self.assertEquals(
            'fa:{}'.format(self.dossier_responsible),
            fields['form.widgets.opengever-tasktemplates-tasktemplate.responsible'])

    @browsing
    def test_replace_interactive_responsible(self, browser):
        self.login(self.regular_user, browser=browser)

        ITaskTemplate(self.tasktemplate).responsible = 'current_user'
        ITaskTemplate(self.tasktemplate).responsible_client = INTERACTIVE_USERS
        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'])

        main_task = self.dossier.listFolderContents()[-1]
        subtask = main_task.listFolderContents()[0]
        self.assertEquals(self.regular_user.getId(), subtask.responsible)

    @browsing
    def test_set_relateditems_on_every_subtask_when_selected(self, browser):
        self.login(self.regular_user, browser=browser)

        ITaskTemplate(self.tasktemplate).responsible = 'current_user'
        ITaskTemplate(self.tasktemplate).responsible_client = INTERACTIVE_USERS

        self.trigger_tasktemplatefolder(
            browser, templates=['Arbeitsplatz einrichten.'],
            documents=[self.document])

        main_task = self.dossier.get('task-1')
        subtask = main_task.listFolderContents()[0]

        self.assertEquals(
            [self.document],
            [relation.to_object for relation in subtask.relatedItems])

    @browsing
    def test_initial_state_is_open_for_parallel_folders(self, browser):
        self.login(self.regular_user, browser=browser)
        self.tasktemplatefolder.sequence_type = u'parallel'

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        self.trigger_tasktemplatefolder(
            browser,
            templates=['Arbeitsplatz einrichten.', 'Notebook einrichten.'],
            documents=[self.document])

        main_task = self.dossier.objectValues()[-1]

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))
        self.assertEquals(
            ['task-state-open', 'task-state-open'],
            [api.content.get_state(task) for task in main_task.objectValues()])

    @browsing
    def test_initial_state_is_planned_for_sequential_folders(self, browser):
        self.login(self.regular_user, browser=browser)
        self.tasktemplatefolder.sequence_type = u'sequential'

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        self.trigger_tasktemplatefolder(
            browser,
            templates=['Arbeitsplatz einrichten.', 'Notebook einrichten.'],
            documents=[self.document], start_immediately=False)

        main_task = self.dossier.objectValues()[-1]

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))
        self.assertEquals(
            ['task-state-planned', 'task-state-planned'],
            [api.content.get_state(task) for task in main_task.objectValues()])

    @browsing
    def test_respects_start_immediately_flag(self, browser):
        self.login(self.regular_user, browser=browser)
        self.tasktemplatefolder.sequence_type = u'sequential'

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        self.trigger_tasktemplatefolder(
            browser,
            templates=['Arbeitsplatz einrichten.', 'Notebook einrichten.'],
            documents=[self.document], start_immediately=True)

        main_task = self.dossier.objectValues()[-1]

        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))
        self.assertEquals(
            ['task-state-open', 'task-state-planned'],
            [api.content.get_state(task) for task in main_task.objectValues()])

    @browsing
    def test_sets_task_templatefolder_predecessor(self, browser):
        self.login(self.regular_user, browser=browser)
        self.tasktemplatefolder.sequence_type = u'sequential'

        create(Builder('tasktemplate')
               .titled(u'Notebook einrichten.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
        .within(self.tasktemplatefolder))

        create(Builder('tasktemplate')
               .titled(u'User Accounts erstellen.')
               .having(issuer='responsible',
                       responsible_client='fa',
                       responsible='robert.ziegler',
                       deadline=10,
                       preselected=True)
               .within(self.tasktemplatefolder))

        self.trigger_tasktemplatefolder(
            browser, templates=[u'Arbeitsplatz einrichten.',
                                u'Notebook einrichten.',
                                u'User Accounts erstellen.'])

        main_task = self.dossier.listFolderContents()[-1]
        ids = main_task.objectIds()
        task1, task2, task3 = [main_task.get(_id) for _id in ids]

        self.assertEquals(
            [task1, task2, task3],
            [oguid.resolve_object() for oguid in main_task.get_tasktemplate_order()])

        self.assertEquals(task1.get_sql_object(),
                          task2.get_sql_object().get_previous_task())
        self.assertEquals(task3.get_sql_object(),
                          task2.get_sql_object().get_next_task())

    @browsing
    def test_add_form_does_not_list_shadow_documents_as_relatable(self, browser):
        """Dossier responsible has created the shadow document.

        This test ensures he does not get it offered as a relatable document on
        tasktemplates.
        """
        self.login(self.dossier_responsible, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            'add-tasktemplate',
            '++widget++form.widgets.related_documents',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [
            '2015',
            '2016',
            '[No Subject]',
            u'Die B\xfcrgschaft',
            u'Initialvertrag f\xfcr Bearbeitung',
            u'L\xe4\xe4r',
            'Personaleintritt',
            u'Vertr\xe4gsentwurf',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentw\xfcrfe 2018',
        ]
        self.assertEqual(expected_documents, browser.css('li').text)
