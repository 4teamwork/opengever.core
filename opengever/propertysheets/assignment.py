from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX = "IDocumentMetadata.document_type"
DOCUMENT_DEFAULT_ASSIGNMENT_SLOT = "IDocument.default"

DOSSIER_TYPE_ASSIGNMENT_SLOT_PREFIX = "IDossier.dossier_type"
DOSSIER_DEFAULT_ASSIGNMENT_SLOT = "IDossier.default"


@implementer(IVocabularyFactory)
class PropertySheetAssignmentVocabulary(object):
    """Factory for vocabulary of all valid property sheet assignment slots."""
    def __call__(self, context):
        assignment_terms = []
        for slot_name in get_document_assignment_slots():
            assignment_terms.append(SimpleTerm(slot_name))

        for slot_name in get_dossier_assignment_slots():
            assignment_terms.append(SimpleTerm(slot_name))

        return SimpleVocabulary(assignment_terms)


def get_document_assignment_slots():
    """"Return a list of all valid assignment slots for documents.

    This is limited to one slot per possible value of the
    `document_type` field and the default document slot.
    """
    vocabulary_factory = getUtility(
        IVocabularyFactory, name="opengever.document.document_types"
    )
    terms = [
        document_type_assignment_slot_name(term.value)
        for term in vocabulary_factory(None)
    ]

    return [DOCUMENT_DEFAULT_ASSIGNMENT_SLOT] + terms


def document_type_assignment_slot_name(value):
    return u"{}.{}".format(
        DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
        value
    )


def get_dossier_assignment_slots():
    """"Return a list of all valid assignment slots for dossiers.

    This is limited to one slot per possible value of the
    `dossier_type` field and the default dossier slot.
    """
    vocabulary_factory = getUtility(
        IVocabularyFactory, name="opengever.dossier.dossier_types"
    )
    terms = [
        dossier_type_assignment_slot_name(term.value)
        for term in vocabulary_factory(None)
    ]

    return [DOSSIER_DEFAULT_ASSIGNMENT_SLOT] + terms


def dossier_type_assignment_slot_name(value):
    return u"{}.{}".format(DOSSIER_TYPE_ASSIGNMENT_SLOT_PREFIX, value)
