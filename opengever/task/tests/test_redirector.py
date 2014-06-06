from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskRedirector(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestTaskRedirector, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.dossier = create(Builder('dossier'))

    def test_redirects_to_dossiers_task_tab_when_creating_a_maintask(self):
        self.create_task(self.dossier, 'Main task')

        self.browser.assert_url('%s#tasks' % self.dossier.absolute_url())

    def test_redirects_to_maintask_overview_tab_when_creating_a_subtask(self):

        task = create(Builder('task')
                      .within(self.dossier)
                      .having(title='Subtask',
                              task_type='approval',
                              responsible=TEST_USER_ID,
                              issuer=TEST_USER_ID)
                      .in_state('task-state-in-progress'))

        self.create_task(task, 'Subtask')

        self.browser.assert_url('%s#overview' % task.absolute_url())

    def create_task(self, container, title, task_type='For direct execution',
                    responsible_name='Test', responsible_id=TEST_USER_ID):

        self.browser.open(
            '%s/++add++opengever.task.task' % container.absolute_url())

        self.browser.fill({'Title': title})
        self.browser.getControl(task_type).selected = True
        self.browser.getControl(
            name='form.widgets.responsible.widgets.query').value = responsible_name
        self.browser.click('form.widgets.responsible.buttons.search')
        self.browser.getControl(
            name='form.widgets.responsible:list').value = [responsible_id]
        self.browser.click('Save')
