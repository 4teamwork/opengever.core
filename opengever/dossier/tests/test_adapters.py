from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.component import getAdapter


class TestParentDossierFinder(FunctionalTestCase):

    def test_find_dossier_returns_first_dossierish_parent(self):
        dossier = create(Builder('dossier'))
        document_1 = create(Builder('document').within(dossier))

        subdossier = create(Builder('dossier').within(dossier))
        document_2 = create(Builder('document').within(subdossier))

        finder = getAdapter(document_1, name='parent-dossier-finder')
        self.assertEquals(dossier, finder.find_dossier())

        finder = getAdapter(document_2, name='parent-dossier-finder')
        self.assertEquals(subdossier, finder.find_dossier())

    def test_find_dossier_works_for_tasks_and_subtask(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))
        subtask = create(Builder('task').within(task))

        finder = getAdapter(task, name='parent-dossier-finder')
        self.assertEquals(dossier, finder.find_dossier())
        finder = getAdapter(subtask, name='parent-dossier-finder')
        self.assertEquals(dossier, finder.find_dossier())

    def test_find_dossier_handles_document_inside_a_task_correclty(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))
        document = create(Builder('document').within(task))

        finder = getAdapter(document, name='parent-dossier-finder')
        self.assertEquals(dossier, finder.find_dossier())
