from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from StringIO import StringIO
import transaction


class TestTaskOverview(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestTaskOverview, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit()
            .with_admin_unit(public_url='http://plone'))

    @browsing
    def test_issuer_is_linked_to_issuers_details_view(self, browser):
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/@@user-details/test_user_1_',
            browser.css('.issuer a').first.get('href'))

    @browsing
    def test_issuer_is_labeld_by_user_description(self, browser):
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            self.user.label(), browser.css('.issuer a').first.text)

    @browsing
    def test_issuer_is_prefixed_by_current_org_unit_on_a_multiclient_setup(self, browser): # noqa
        create(Builder('org_unit').id('client2')
               .having(admin_unit=self.admin_unit))
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'Client1 / Test User (test_user_1_)',
            browser.css('.issuer').first.text)

    @browsing
    def test_date_of_completion_is_displayed_correclty(self, browser):
        task = create(Builder("task")
                      .having(task_type='comment',
                              date_of_completion=date(2015, 2, 2),
                              issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        main_attributes_table = browser.css('#main_attributesBox .listing').first  #noqa
        date_of_completion_row = main_attributes_table.lists()[-1]
        self.assertEquals(['Date of completion', 'Feb 02, 2015'],
                          date_of_completion_row)

    @browsing
    def test_documents_are_listed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        create(Builder('document')
               .titled(u'Some document')
               .within(task))

        browser.login().open(task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Some document'],
            browser.css('#documentsBox a.document_link').text)

    @browsing
    def test_zip_export_actions_are_available(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID,))

        create(Builder('document')
               .titled(u'Some document')
               .within(task))

        browser.login().open(task)

        self.assertIsNotNone(
            browser.css('.actionicon-object_buttons-zipexport'))

        browser.open(task, view='tabbedview_view-documents')

        self.assertIn('Export as Zip',
                      browser.css('#plone-contentmenu-tabbedview-actions li')
                      .text)

    @browsing
    def test_can_export_zip(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID,))

        document = create(Builder('document')
                          .titled(u'Some document')
                          .within(task)
                          .with_dummy_content())

        data = {'zip_selected:method': 1,
                'paths:list': ['/'.join(document.getPhysicalPath())]}

        browser.login().open(task, view='zip_export')

        zipfile = ZipFile(StringIO(browser.contents), 'r')

        self.assertEquals([document.file.filename], zipfile.namelist())

        browser.open(task, data=data)

        zipfile = ZipFile(StringIO(browser.contents), 'r')

        self.assertEquals([document.file.filename], zipfile.namelist())

    @browsing
    def test_task_overview_displays_task_information(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        browser.login().open(task, view='tabbedview_view-overview')

        table_data = [
            each[1] for each in
            browser.css('#main_attributesBox table.vertical.listing')
            .first.lists()
        ]

        self.assertSequenceEqual(
            ['Aufgabe', 'Dossier', 'Text blabla', 'To comment',
             'task-state-open', 'January 1, 2010', self.user.label(),
             self.user.label(), ''],
            table_data
        )

    @browsing
    def test_task_text_linebreaks_are_transformed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        text = 'Description\nThis is a description'

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text=text,
                              task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        expected = u'Description<br>This is a description'
        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_task_text_simple_urls_in_sentences_are_transformed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        text = 'Is http://u.rl.\nIs http://u.rl?\nIs http://u.rl!'

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text=text,
                              task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        expected = (u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl" rel="nofollow">http://u.rl</a>!')  # noqa

        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_task_text_urls_in_sentences_are_transformed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        text = 'Is http://u.rl/.\nIs http://u.rl/?\nIs http://u.rl/!'

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text=text,
                              task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        expected = (u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/" rel="nofollow">http://u.rl/</a>!')  # noqa

        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_task_text_urls_with_get_arguments_in_sentences_are_transformed(
            self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        text = ('Is http://u.rl/with?get=arguments.\n'
                'Is http://u.rl/with?get=arguments?\n'
                'Is http://u.rl/with?get=arguments!\n'
                'Is http://u.rl/with?sev=eral&get=args.\n'
                'Is http://u.rl/with?sev=eral&get=args?\n'
                'Is http://u.rl/with?sev=eral&get=args!')

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text=text,
                              task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

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
    def test_task_text_urls_with_anchors_in_sentences_are_transformed(
            self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))

        text = ('Is http://u.rl/with#goto.\n'
                'Is http://u.rl/with#goto?\n'
                'Is http://u.rl/with#goto!')

        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text=text,
                              task_type='comment'))

        browser.login().open(task, view='tabbedview_view-overview')

        expected = (u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>.<br>'  # noqa
                    u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>?<br>'  # noqa
                    u'Is <a href="http://u.rl/with#goto" rel="nofollow">http://u.rl/with#goto</a>!')  # noqa

        result = (browser.css('table.listing').find('Text').first.row
                         .css('td').first.innerHTML)

        self.assertEqual(expected, result)

    @browsing
    def test_subtasks_are_shown_on_parent_task_page(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Parent')
                      .having(text='Text blabla',
                              task_type='report',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        create(Builder("task")
               .within(task)
               .titled(u'Subtask 1')
               .having(task_type='report',
                       issuer=TEST_USER_ID,
                       responsible=TEST_USER_ID))
        create(Builder("task")
               .within(task)
               .titled(u'Subtask 2')
               .having(task_type='report',
                       issuer=TEST_USER_ID,
                       responsible=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')
        self.assertSequenceEqual(['Subtask 1', 'Subtask 2'],
                                 browser.css('#sub_taskBox div.task').text)
        self.assertSequenceEqual(
            [], browser.css('#containing_taskBox div.task').text)

    @browsing
    def test_parent_task_is_shown_on_subtask_page(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Parent')
                      .having(text='Text blabla',
                              task_type='report',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        sub = create(Builder("task")
                     .within(task)
                     .titled(u'Subtask 1')
                     .having(task_type='report',
                             issuer=TEST_USER_ID,
                             responsible=TEST_USER_ID))

        browser.login().open(sub, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Parent'], browser.css('#containing_taskBox div.task').text)

        self.assertSequenceEqual(
            [], browser.css('#sub_taskBox div.task').text)

    @browsing
    def test_predecessor_successor_tasks_are_shown(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        predecessor = create(Builder("task")
                             .within(dossier)
                             .titled(u'Predecessor')
                             .having(text='Text blabla',
                                     task_type='report',
                                     deadline=datetime(2010, 1, 1),
                                     issuer=TEST_USER_ID,
                                     responsible=TEST_USER_ID))
        successor = create(Builder("task")
                           .within(dossier)
                           .titled(u'Successor')
                           .successor_from(predecessor)
                           .having(task_type='report',
                                   issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID))

        browser.login().open(predecessor, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Successor'], browser.css("#successor_tasksBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("predecessor_taskBox div.task").text)

        browser.login().open(successor, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Predecessor'], browser.css("#predecessor_taskBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("#successor_tasksBox div.task").text)

    @browsing
    def test_state_is_translated_state_label(self, browser):
        self.task = create(Builder('task')
                           .in_state('task-state-tested-and-closed'))

        # set french as preferred language
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.addSupportedLanguage('fr-ch')
        lang_tool.setDefaultLanguage('fr-ch')
        transaction.commit()

        browser.login().open(self.task, view='tabbedview_view-overview')

        self.assertIn(['Etat', u'Ferm\xe9'],
                      browser.css('table.listing').first.lists())
