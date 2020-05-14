from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.testing import IntegrationTestCase


class TestTaskTemplateActivites(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_record_activity_for_all_subtasks(self, browser):
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
        browser.fill({'Tasktemplatefolder': u'Verfahren Neuanstellung'})
        browser.click_on('Continue')

        browser.fill({'Tasktemplates': ['Arbeitsplatz einrichten.',
                                        u'Notebook einrichten.']})

        browser.click_on('Continue')
        browser.click_on('Trigger')

        main_task = self.dossier.objectValues()[-1]
        seq1, seq2 = main_task.objectValues()

        self.assertItemsEqual(
            [main_task, main_task, seq1, seq2],
            [activity.resource.oguid.resolve_object() for activity in Activity.query.all()])

        self.assertItemsEqual(
            [u'task-added', u'task-transition-open-in-progress', u'task-added', u'task-added'],
            [activity.kind for activity in Activity.query.all()])

    @browsing
    def test_does_not_record_activity_for_planed_task(self, browser):
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

        browser.open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': u'Verfahren Neuanstellung'})
        browser.click_on('Continue')

        browser.fill({'Tasktemplates': ['Arbeitsplatz einrichten.',
                                        u'Notebook einrichten.']})

        browser.click_on('Continue')
        browser.click_on('Trigger')

        main_task = self.dossier.objectValues()[-1]
        seq1, seq2 = main_task.objectValues()

        self.assertItemsEqual([
          (u'task-added', main_task),
          (u'task-transition-open-in-progress', main_task),
          (u'task-added', seq1)],
          [(activity.kind, activity.resource.oguid.resolve_object())
           for activity in Activity.query.all()])
