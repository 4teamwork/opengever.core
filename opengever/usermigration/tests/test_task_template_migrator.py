from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.usermigration.task_templates import TaskTemplateMigrator


class TestTaskTemplateMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestTaskTemplateMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

    def test_migrates_plone_tasktemplate_responsibles(self):
        tasktemplate = create(Builder('tasktemplate')
                      .having(responsible='HANS.MUSTER'))

        TaskTemplateMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', tasktemplate.responsible)

    def test_migrates_plone_tasktemplate_issuers(self):
        tasktemplate = create(Builder('tasktemplate')
                      .having(issuer='HANS.MUSTER'))

        TaskTemplateMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', tasktemplate.issuer)
