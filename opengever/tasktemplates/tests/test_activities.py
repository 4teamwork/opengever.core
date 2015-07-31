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

        self.template_dossier = create(Builder('templatedossier'))
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_record_activity_for_the_maintask_and_all_subtasks(self, browser):
        template_folder = create(Builder('tasktemplatefolder')
                                 .within(self.template_dossier)
                                 .in_state('tasktemplatefolder-state-activ')
                                 .titled(u'Mitberichtsverfahren'))
        tasktemplate_1 =  create(Builder('tasktemplate')
                                 .within(template_folder)
                                 .titled(u'Einladung zum Mitbericht versenden'))
        tasktemplate_2 =  create(Builder('tasktemplate')
                                 .within(template_folder)
                                 .titled(u'Mitberichte zusammenfassen.'))
        tasktemplate_3 =  create(Builder('tasktemplate')
                                 .within(template_folder)
                                 .titled(u'Endg\xfcltige Stellungnahme versenden'))

        browser.login().open(self.dossier)

        paths = ['/'.join(document.getPhysicalPath()) for
                 document in (tasktemplate_1, tasktemplate_2, tasktemplate_3)]
        browser.open(self.dossier, {'paths': paths}, view='add-tasktemplate/create')

        self.assertEquals(4, len(Activity.query.all()))
        self.assertEquals(
            [u'Einladung zum Mitbericht versenden',
             u'Mitberichte zusammenfassen.',
             u'Endg\xfcltige Stellungnahme versenden',
             u'Mitberichtsverfahren'],
            [activity.title for activity in Activity.query.all()])
