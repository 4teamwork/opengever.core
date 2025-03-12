from opengever.propertysheets.assignment import get_document_assignment_slots
from opengever.propertysheets.assignment import get_dossier_assignment_slots
from opengever.testing.test_case import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


EXPECTED_DOCUMENT_ASSIGNMENT_SLOTS = [
    u"IDocumentMetadata.document_type.contract",
    u"IDocumentMetadata.document_type.directive",
    u"IDocumentMetadata.document_type.offer",
    u"IDocumentMetadata.document_type.protocol",
    u"IDocumentMetadata.document_type.question",
    u"IDocumentMetadata.document_type.regulations",
    u"IDocumentMetadata.document_type.report",
    u"IDocumentMetadata.document_type.request",
    u"IDocumentMetadata.document_type.costs-statement",
    u"IDocumentMetadata.document_type.credit-note",
    u"IDocumentMetadata.document_type.supplementary-agreement",

]

EXPECTED_DOCUMENT_DEFAULT_SLOT = [
    u"IDocument.default",
]

EXPECTED_DOSSIER_DEFAULT_SLOT = [
    u"IDossier.default",
]

EXPECTED_DOSSIER_ASSIGNMENT_SLOTS = [
    u"IDossier.dossier_type.businesscase",
]


class TestPropertySheetAssignmentVocabulary(FunctionalTestCase):

    def test_assignemnt_vocabulary_contains_document_types(self):
        vocabulary = getUtility(
            IVocabularyFactory,
            name="opengever.propertysheets.PropertySheetAssignmentsVocabulary",
        )(self.portal)

        expected = EXPECTED_DOCUMENT_DEFAULT_SLOT + \
            EXPECTED_DOCUMENT_ASSIGNMENT_SLOTS + \
            EXPECTED_DOSSIER_DEFAULT_SLOT + \
            EXPECTED_DOSSIER_ASSIGNMENT_SLOTS

        self.assertItemsEqual(expected, [term.value for term in vocabulary])


class TestPropertySheetDocumentAssignmentSlots(FunctionalTestCase):

    def test_assignemnt_vocabulary_contains_document_types(self):
        self.assertItemsEqual(
            EXPECTED_DOCUMENT_DEFAULT_SLOT + EXPECTED_DOCUMENT_ASSIGNMENT_SLOTS,
            get_document_assignment_slots(),
        )


class TestPropertySheetDossierAssignmentSlots(FunctionalTestCase):

    def test_assignemnt_vocabulary_contains_dossier_types(self):
        self.assertItemsEqual(
            EXPECTED_DOSSIER_DEFAULT_SLOT + EXPECTED_DOSSIER_ASSIGNMENT_SLOTS,
            get_dossier_assignment_slots(),
        )
