from datetime import datetime
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from ftw.testing import MockTestCase
from opengever.latex import dossiertasks
from opengever.latex.dossiertasks import provide_dossier_task_layer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.testing import LATEX_ZCML_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDossierTasksPDFView(MockTestCase):

    layer = LATEX_ZCML_LAYER

    def test_is_registered(self):
        context = self.create_dummy()
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()
        view = getMultiAdapter((context, request), name='pdf-dossier-tasks')
        self.assertTrue(isinstance(view, dossiertasks.DossierTasksPDFView))


class TestDossierTasksLaTeXView(FunctionalTestCase):

    @browsing
    def test_dossier_tasks_label(self, browser):
        dossier = create(Builder('dossier').titled(u'Anfr\xf6gen 2015'))

        with provide_dossier_task_layer(dossier.REQUEST):
            layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
            dossier_tasks = getMultiAdapter(
                (dossier, dossier.REQUEST, layout), ILaTeXView)

            self.assertEquals(
                'Task list for dossier "`Anfr\xc3\xb6gen 2015 (Client1 / 1)"\'',
                dossier_tasks.get_render_arguments().get('label'))

    @browsing
    def test_dossier_tasks_data(self, browser):
        repository = create(Builder('repository_root')
                            .titled(u'Repository'))
        dossier = create(Builder('dossier')
                         .titled(u'Anfr\xf6gen 2015')
                         .within(repository)
                         .having(responsible=self.user.userid))

        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .titled(u'Subdossier'))

        with freeze(datetime(2016, 4, 12, 10, 35)):
            task1 = create(Builder('task')
                           .within(dossier)
                           .having(responsible=self.user.userid,
                                   issuer=SITE_OWNER_NAME,
                                   title="task 1"))

            task2 = create(Builder('task')
                           .within(subdossier)
                           .having(responsible=self.user.userid,
                                   issuer=self.user.userid,
                                   title="task 2"))

        expected_deadline = datetime(2016, 4, 17, 0, 0)

        with freeze(datetime(2016, 10, 12, 13, 20)):
            api.content.transition(task1, to_state='task-state-resolved')
            completion_date = date.today()

        with provide_dossier_task_layer(dossier.REQUEST):
            layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
            dossiertasks = getMultiAdapter((dossier, dossier.REQUEST, layout),
                                           ILaTeXView)
            self.assertEquals([task1, task2], dossiertasks.get_tasks())

            expected = {'label': 'Task list for dossier "`Anfr\xc3\xb6gen 2015 (Client1 / 1)"\'',
                        'task_data_list': [{'completion_date': completion_date.strftime('%d.%m.%Y'),
                                            'deadline': expected_deadline.strftime('%d.%m.%Y'),
                                            'description': '',
                                            'responsible': 'Test User (test\\_user\\_1\\_)',
                                            'issuer': 'admin (admin)',
                                            'sequence_number': 1,
                                            'title': 'task 1',
                                            'type': ''},
                                           {'completion_date': None,
                                            'deadline': expected_deadline.strftime('%d.%m.%Y'),
                                            'description': '',
                                            'responsible': 'Test User (test\\_user\\_1\\_)',
                                            'issuer': 'Test User (test\\_user\\_1\\_)',
                                            'sequence_number': 2,
                                            'title': 'task 2',
                                            'type': ''}]}

            values = dossiertasks.get_render_arguments()
            # remove history attribute from the dicts, history is tested in
            # a separate test
            [item.pop('history') for item in values['task_data_list']]

            self.assertEquals(expected['label'], values['label'])
            self.assertEquals(expected['task_data_list'], values['task_data_list'])

    @browsing
    def test_dossier_tasks_history(self, browser):
        repository = create(Builder('repository_root')
                            .titled(u'Repository'))
        dossier = create(Builder('dossier')
                         .titled(u'Anfr\xf6gen 2015')
                         .within(repository)
                         .having(responsible=self.user.userid))

        browser.login().visit(dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Task title',
                      'Task Type': 'To comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(TEST_USER_ID)
        browser.find('Save').click()

        browser.open('http://nohost/plone/repository/dossier-1/task-1')
        browser.click_on("task-transition-open-resolved")
        browser.fill({'Response': 'response text'})
        browser.click_on("Save")

        with provide_dossier_task_layer(dossier.REQUEST):
            layout = DefaultLayout(dossier, dossier.REQUEST, PDFBuilder())
            dossiertasks = getMultiAdapter((dossier, dossier.REQUEST, layout),
                                           ILaTeXView)
            tasks_data = dossiertasks.get_render_arguments()['task_data_list']
            self.assertEqual(1, len(tasks_data))
            self.assertIn("response text", tasks_data[0]['history'])
