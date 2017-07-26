from opengever.testing import IntegrationTestCase
from zope.component import getAdapter


class TestParentDossierFinder(IntegrationTestCase):

    def test_find_dossier_returns_first_dossierish_parent(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            self.dossier,
            getAdapter(self.document,
                       name='parent-dossier-finder').find_dossier())

        self.assertEquals(
            self.subdossier,
            getAdapter(self.subdocument,
                       name='parent-dossier-finder').find_dossier())

    def test_find_dossier_works_for_tasks_and_subtask(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            self.dossier,
            getAdapter(self.task,
                       name='parent-dossier-finder').find_dossier())

        self.assertEquals(
            self.dossier,
            getAdapter(self.subtask,
                       name='parent-dossier-finder').find_dossier())

    def test_find_dossier_handles_document_inside_a_task_correctly(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            self.dossier,
            getAdapter(self.taskdocument,
                       name='parent-dossier-finder').find_dossier())
