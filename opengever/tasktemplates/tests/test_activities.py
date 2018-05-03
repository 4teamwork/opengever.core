from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase


class TestTaskTemplateActivites(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestTaskTemplateActivites, self).setUp()

        self.template_folder = create(Builder('templatefolder'))
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_record_activity_for_the_maintask_and_all_subtasks(self, browser):
        template_folder = create(Builder('tasktemplatefolder')
                                 .within(self.template_folder)
                                 .in_state('tasktemplatefolder-state-activ')
                                 .titled(u'Mitberichtsverfahren'))
        create(Builder('tasktemplate')
               .within(template_folder)
               .titled(u'Einladung zum Mitbericht versenden')
               .having(preselected=True))
        create(Builder('tasktemplate')
               .within(template_folder)
               .titled(u'Mitberichte zusammenfassen.')
               .having(preselected=True))
        create(Builder('tasktemplate')
               .within(template_folder)
               .titled(u'Endg\xfcltige Stellungnahme versenden')
               .having(preselected=True))

        browser.login().open(self.dossier, view='add-tasktemplate')
        browser.fill({'Tasktemplatefolder': u'Mitberichtsverfahren'})
        browser.click_on('Continue')

        browser.click_on('Continue')
        browser.click_on('Trigger')

        self.assertItemsEqual(
            [u'Einladung zum Mitbericht versenden',
             u'Mitberichte zusammenfassen.',
             u'Endg\xfcltige Stellungnahme versenden'],
            [activity.title for activity in Activity.query.all()])
