from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import IntegrationTestCase
from plone import api
from StringIO import StringIO
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class TestTaskOverview(IntegrationTestCase):

    @browsing
    def test_issuer_is_linked_to_issuers_details_view(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/@@user-details/robert.ziegler',
            browser.css('.issuer a').first.get('href'))

    @browsing
    def test_issuer_is_labeld_by_user_description(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, view='tabbedview_view-overview')

        self.assertEquals('Ziegler Robert (robert.ziegler)',
                          browser.css('.issuer a').first.text)

    @browsing
    def test_issuer_is_prefixed_by_current_org_unit_on_a_multiclient_setup(self, browser): # noqa
        self.login(self.regular_user, browser=browser)
        create(Builder('org_unit').id('client2')
               .having(admin_unit=get_current_admin_unit()))
        browser.open(self.task, view='tabbedview_view-overview')

        self.assertEquals(
            'Finanzamt / Ziegler Robert (robert.ziegler)',
            browser.css('.issuer').first.text)

    @browsing
    def test_date_of_completion_is_displayed_correclty(self, browser):
        self.login(self.regular_user, browser=browser)

        self.task.date_of_completion = date(2015, 2, 2)
        self.task.get_sql_object().completed = date(2015, 2, 2)

        browser.open(self.task, view='tabbedview_view-overview')

        main_attributes_table = browser.css('#main_attributesBox .listing').first  #noqa
        date_of_completion_row = main_attributes_table.lists()[-1]
        self.assertEquals(['Date of completion', 'Feb 02, 2015'],
                          date_of_completion_row)

    @browsing
    def test_documents_are_listed(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Feedback zum Vertragsentwurf', u'Vertr\xe4gsentwurf'],
            browser.css('#documentsBox a.document_link').text)

    @browsing
    def test_zip_export_actions_are_available(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task)
        self.assertIsNotNone(
            browser.css('.actionicon-object_buttons-zipexport'))

        browser.open(self.task, view='tabbedview_view-documents')
        self.assertIn(
            'Export as Zip',
            browser.css('#plone-contentmenu-tabbedview-actions li').text)

    @browsing
    def test_can_export_zip(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='zip_export')
        zipfile = ZipFile(StringIO(browser.contents), 'r')

        self.assertEquals(
            [u'Task - Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen/',
             'feedback-zum-vertragsentwurf.docx'],
            zipfile.namelist())

        data = {'zip_selected:method': 1,
                'paths:list': ['/'.join(self.taskdocument.getPhysicalPath())]}
        browser.open(self.task, data=data)

        zipfile = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            [self.taskdocument.file.filename], zipfile.namelist())

    @browsing
    def test_subtasks_are_shown_on_parent_task_page(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'],
            browser.css('#sub_taskBox div.task').text)
        self.assertSequenceEqual(
            [], browser.css('#containing_taskBox div.task').text)

    @browsing
    def test_parent_task_is_shown_on_subtask_page(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.subtask, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Vertragsentwurf \xdcberpr\xfcfen'],
            browser.css('#containing_taskBox div.task').text)
        self.assertSequenceEqual(
            [], browser.css('#sub_taskBox div.task').text)

    @browsing
    def test_predecessor_successor_tasks_are_shown(self, browser):
        self.login(self.regular_user, browser=browser)

        self.register_successor(self.task, self.archive_task)

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Vertr\xe4ge abschliessen'],
            browser.css("#successor_tasksBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("predecessor_taskBox div.task").text)


        browser.open(self.archive_task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Vertragsentwurf \xdcberpr\xfcfen'],
            browser.css("#predecessor_taskBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("#successor_tasksBox div.task").text)

    @browsing
    def test_state_is_translated_state_label(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.task)

        # set french as preferred language
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.addSupportedLanguage('fr-ch')
        lang_tool.setDefaultLanguage('fr-ch')

        browser.open(self.task, view='tabbedview_view-overview')
        self.assertIn(['Etat', u'Ferm\xe9'],
                      browser.css('table.listing').first.lists())


class TestTaskFromTasktemplateFolderOverview(IntegrationTestCase):

    @browsing
    def test_subtask_box_contains_sequence_type_label(self, browser):
        self.login(self.regular_user, browser=browser)

        # sequential
        alsoProvides(self.task, IFromSequentialTasktemplate)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            [u'Sequential process'],
            browser.css('#sub_taskBox .sequence_type').text)

        # parallel
        noLongerProvides(self.task, IFromSequentialTasktemplate)
        alsoProvides(self.task, IFromParallelTasktemplate)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            [u'Parallel process'],
            browser.css('#sub_taskBox .sequence_type').text)

    @browsing
    def test_subtask_contains_sequence_type_class(self, browser):
        self.login(self.regular_user, browser=browser)

        # sequential
        alsoProvides(self.task, IFromSequentialTasktemplate)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            'task-container sequential',
            browser.css('#sub_taskBox div').first.get('class'))

        # parallel
        noLongerProvides(self.task, IFromSequentialTasktemplate)
        alsoProvides(self.task, IFromParallelTasktemplate)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertEquals(
            'task-container parallel',
            browser.css('#sub_taskBox div').first.get('class'))

    @browsing
    def test_subtask_contains_sequence_type_class(self, browser):
        self.login(self.regular_user, browser=browser)

        self.subtask.set_tasktemplate_predecessor(self.archive_task)
        self.subtask.get_sql_object().sync_with(self.subtask)

        self.inactive_task.set_tasktemplate_predecessor(self.subtask)
        self.inactive_task.get_sql_object().sync_with(self.inactive_task)

        # sequential
        alsoProvides(self.subtask, IFromSequentialTasktemplate)

        browser.open(self.subtask, view='tabbedview_view-overview')
        self.assertEquals(
            [self.archive_task.title],
            browser.css('#sequence_taskBox .previous_task .task').text)

        self.assertEquals(
            [self.inactive_task.title],
            browser.css('#sequence_taskBox .next_task .task').text)


class TestTaskTextTransformation(IntegrationTestCase):

    @browsing
    def test_task_overview_displays_task_information(self, browser):
        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = u'Der Entwurf befindet sich im Anhang'

        browser.open(self.task, view='tabbedview_view-overview')
        table_data = [
            each[1] for each in
            browser.css('#main_attributesBox table.vertical.listing')
            .first.lists()]

        self.assertSequenceEqual(
            [u'Vertragsentwurf \xdcberpr\xfcfen',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'Der Entwurf befindet sich im Anhang',
             'For confirmation / correction',
             'task-state-in-progress',
             'November 1, 2016',
             'Ziegler Robert (robert.ziegler)',
             u'B\xe4rfuss K\xe4thi (kathi.barfuss)', ''],
            table_data)

    @browsing
    def test_task_text_linebreaks_are_transformed(self, browser):
        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = u'Description\nThis is a description'

        browser.open(self.task, view='tabbedview_view-overview')
        expected = u'Description<br>This is a description'
        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_task_text_simple_urls_in_sentences_are_transformed(self, browser):
        text = 'Is http://u.rl.\nIs http://u.rl?\nIs http://u.rl!'

        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = text

        browser.open(self.task, view='tabbedview_view-overview')
        expected = (u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>!')  # noqa
        result = (browser.css('table.listing').find('Text').first.row
                  .css('td').first.innerHTML)
        self.assertEqual(expected, result)

    @browsing
    def test_task_text_urls_in_sentences_are_transformed(self, browser):
        text = 'Is http://u.rl/.\nIs http://u.rl/?\nIs http://u.rl/!'

        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = text

        browser.open(self.task, view='tabbedview_view-overview')
        expected = (u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>!')  # noqa
        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)
        self.assertEqual(expected, result)

    @browsing
    def test_task_text_urls_with_get_arguments_in_sentences_are_transformed(self, browser):

        text = ('Is http://u.rl/with?get=arguments.\n'
                'Is http://u.rl/with?get=arguments?\n'
                'Is http://u.rl/with?get=arguments!\n'
                'Is http://u.rl/with?sev=eral&get=args.\n'
                'Is http://u.rl/with?sev=eral&get=args?\n'
                'Is http://u.rl/with?sev=eral&get=args!')

        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = text

        browser.open(self.task, view='tabbedview_view-overview')
        expected = (u'Is <a href="http://u.rl/with?get=arguments" rel="nofollow">http://u.rl/with?get=arguments</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/with?get=arguments" rel="nofollow">http://u.rl/with?get=arguments</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/with?get=arguments" rel="nofollow">http://u.rl/with?get=arguments</a>!<br>'  # noqa
                    u'Is <a href="http://u.rl/with?sev=eral&amp;get=args" rel="nofollow">http://u.rl/with?sev=eral&amp;get=args</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/with?sev=eral&amp;get=args" rel="nofollow">http://u.rl/with?sev=eral&amp;get=args</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/with?sev=eral&amp;get=args" rel="nofollow">http://u.rl/with?sev=eral&amp;get=args</a>!')  # noqa

        result = (browser.css('table.listing').find('Text').first.row
                  .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_task_text_urls_with_anchors_in_sentences_are_transformed(self, browser):
        text = ('Is http://u.rl/with#goto.\n'
                'Is http://u.rl/with#goto?\n'
                'Is http://u.rl/with#goto!')

        self.login(self.regular_user, browser=browser)
        self.task.get_sql_object().text = text

        browser.open(self.task, view='tabbedview_view-overview')

        expected = (u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>!')  # noqa
        result = (browser.css('table.listing').find('Text').first.row
                  .css('td').first.innerHTML)
        self.assertEqual(expected, result)
