from ftw.builder import Builder
from ftw.builder import create
from opengever.task.sources import DocumentsFromTaskSource
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestTaskSources(IntegrationTestCase):

    def test_docs_from_task_source_contains_related_and_contained(self):
        self.login(self.dossier_responsible)

        contained_doc = create(
            Builder('document')
            .titled(u'Sanierung B\xe4rengraben.docx')
            .within(self.subtask))

        self.assertEqual(1, len(self.subtask.relatedItems))
        related_doc = self.subtask.relatedItems[0].to_object

        source = DocumentsFromTaskSource(self.subtask)

        self.assertIn(IUUID(contained_doc), source)
        self.assertIn(IUUID(related_doc), source)

        self.assertItemsEqual(
            [IUUID(contained_doc), IUUID(related_doc)],
            source.all_uids,
        )
