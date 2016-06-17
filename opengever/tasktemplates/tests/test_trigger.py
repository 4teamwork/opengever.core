from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
import transaction


class TestTriggeringTaskTemplate(FunctionalTestCase):

    def setUp(self):
        super(TestTriggeringTaskTemplate, self).setUp()

        create(Builder('ogds_user').id(u'hugo.boss'))
        create(Builder('ogds_user').id(u'peter.meier'))
        self.dossier = create(Builder('dossier')
                              .having(responsible=u'peter.meier'))
        self.templatedossier = create(Builder('templatedossier'))

        self.folder1 = create(Builder('tasktemplatefolder')
                         .within(self.templatedossier)
                         .titled(u'Mitberichtsverfahren')
                         .in_state('tasktemplatefolder-state-activ'))

        create(Builder('tasktemplate')
               .within(self.folder1)
               .titled(u'Mitbericht FD')
               .having(preselected=True, deadline=17, issuer=u'current_user',
                       responsible_client=u'interactive_users',
                       responsible=u'current_user'))
        create(Builder('tasktemplate')
               .within(self.folder1)
               .titled(u'Mitbericht DI')
               .having(preselected=False, deadline=3, issuer=u'hugo.boss',
                       responsible_client=u'client1',
                       responsible=u'hugo.boss'))
        create(Builder('tasktemplate')
               .within(self.folder1)
               .titled(u'Mitbericht SD')
               .having(preselected=False, deadline=5, issuer=u'responsible',
                       responsible_client=u'interactive_users',
                       responsible=u'responsible'))

    def trigger_tasktemplatefolder(self, browser, folder='Mitberichtsverfahren', templates=[]):
        browser.login().open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': folder})
        browser.click_on('Continue')

        browser.fill({'Tasktemplates': templates})
        browser.click_on('Trigger')

    @browsing
    def test_redirects_back_and_show_statusmessage_when_no_active_tasktemplatefolder_exists(self, browser):
        api.content.transition(
            self.folder1,
            transition='tasktemplatefolder-transition-activ-inactiv')
        transaction.commit()

        browser.login().open(self.dossier, view='add-tasktemplate')
        self.assertEquals(self.dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['Currently there are no active task template folders registered.'],
            error_messages())

    @browsing
    def test_all_active_tasktemplates_are_listed(self, browser):
        create(Builder('tasktemplatefolder')
               .titled(u'Einsprache abarbeiten'))
        create(Builder('tasktemplatefolder')
               .titled(u'Einb\xfcrgerungsverfahren')
               .in_state('tasktemplatefolder-state-activ'))

        browser.login().open(self.dossier, view='add-tasktemplate')

        self.assertEquals(
            [u'Einb\xfcrgerungsverfahren', 'Mitberichtsverfahren'],
            browser.css('#formfield-form-widgets-tasktemplatefolder').first.options)

    @browsing
    def test_step2_list_all_tasktemplates_of_the_selected_folder_and_preselects_them_correctly(self, browser):
        browser.login().open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': 'Mitberichtsverfahren'})
        browser.click_on('Continue')

        self.assertEquals(
            ['Mitbericht FD', 'Mitbericht DI', 'Mitbericht SD'],
            browser.css('#formfield-form-widgets-tasktemplates .option').text)

        self.assertEquals(
            ['Mitbericht FD'],
            browser.css('#formfield-form-widgets-tasktemplates input:checked').getparents().text)

    @browsing
    def test_creates_main_task_assigned_to_current_user(self, browser):
        self.trigger_tasktemplatefolder(
            browser, templates=['Mitbericht FD', 'Mitbericht DI'])

        main_task = self.dossier.get('task-1')
        self.assertEquals(u'Mitberichtsverfahren', main_task.title)
        self.assertEquals(TEST_USER_ID, main_task.responsible)
        self.assertEquals(TEST_USER_ID, main_task.issuer)
        self.assertEquals('direct-execution', main_task.task_type)

    @browsing
    def test_sets_main_task_to_in_progress_state(self, browser):
        self.trigger_tasktemplatefolder(
            browser, templates=['Mitbericht FD', 'Mitbericht DI'])

        main_task = self.dossier.get('task-1')
        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))

    @browsing
    def test_main_task_deadline_is_the_highest_template_deadline_plus_five(self, browser):
        self.trigger_tasktemplatefolder(
            browser, templates=['Mitbericht FD', 'Mitbericht DI'])

        self.assertEquals(date.today() + timedelta(days=17 + 5),
                          self.dossier.get('task-1').deadline)

    @browsing
    def test_all_tasks_are_marked_with_marker_interface(self, browser):
        self.trigger_tasktemplatefolder(
            browser, templates=['Mitbericht FD', 'Mitbericht DI'])

        main_task = self.dossier.get('task-1')
        self.assertTrue(IFromTasktemplateGenerated.providedBy(main_task))

        for subtask in main_task.listFolderContents():
            self.assertTrue(IFromTasktemplateGenerated.providedBy(subtask))

    @browsing
    def test_creates_a_subtask_for_each_selected_template(self, browser):
        self.trigger_tasktemplatefolder(
            browser, templates=['Mitbericht FD', 'Mitbericht SD'])

        main_task = self.dossier.get('task-1')
        self.assertEquals(2, len(main_task.listFolderContents()))

        subtask1, subtask2 = main_task.listFolderContents()
        self.assertEquals('Mitbericht FD', subtask1.title)
        self.assertEquals('Mitbericht SD', subtask2.title)

    @browsing
    def test_replace_interactive_issuer(self, browser):
        self.trigger_tasktemplatefolder(
            browser,
            templates=['Mitbericht FD', 'Mitbericht DI', 'Mitbericht SD'])

        main_task = self.dossier.get('task-1')
        subtask1, subtask2, subtask3 = main_task.listFolderContents()

        # current_user
        self.assertEquals(TEST_USER_ID, subtask1.issuer)

        # not interactive
        self.assertEquals('hugo.boss', subtask2.issuer)

        # responsible
        self.assertEquals('peter.meier', subtask3.issuer)

    @browsing
    def test_replace_interactive_responsibles(self, browser):
        self.trigger_tasktemplatefolder(
            browser,
            templates=['Mitbericht FD', 'Mitbericht DI', 'Mitbericht SD'])

        main_task = self.dossier.get('task-1')
        subtask1, subtask2, subtask3 = main_task.listFolderContents()

        # current_user
        self.assertEquals(TEST_USER_ID, subtask1.responsible)
        self.assertEquals('client1', subtask1.responsible_client)

        # not interactive
        self.assertEquals('hugo.boss', subtask2.responsible)
        self.assertEquals('client1', subtask1.responsible_client)

        # responsible
        self.assertEquals('peter.meier', subtask3.responsible)
        self.assertEquals('client1', subtask1.responsible_client)
