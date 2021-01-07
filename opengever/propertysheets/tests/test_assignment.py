from opengever.testing.test_case import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestPropertySheetAssignmentVocabulary(FunctionalTestCase):
    def test_assignemnt_vocabulary_contains_document_types(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name="opengever.propertysheets.PropertySheetAssignmentsVocabulary",
        )(self.portal)

        self.assertEqual(
            [
                u"IDocumentMetadata.document_type.contract",
                u"IDocumentMetadata.document_type.directive",
                u"IDocumentMetadata.document_type.offer",
                u"IDocumentMetadata.document_type.protocol",
                u"IDocumentMetadata.document_type.question",
                u"IDocumentMetadata.document_type.regulations",
                u"IDocumentMetadata.document_type.report",
                u"IDocumentMetadata.document_type.request",
            ],
            [term.value for term in vocabulary],
        )
