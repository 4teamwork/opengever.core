from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX = "IDocumentMetadata.document_type"


@implementer(IVocabularyFactory)
class PropertySheetAssignmentVocabulary(object):
    """Factory for vocabulary of all valid property sheet assignment slots."""
    def __call__(self, context):
        assignment_terms = []
        for slot_name in get_document_assignment_slots():
            assignment_terms.append(SimpleTerm(slot_name))
        return SimpleVocabulary(assignment_terms)


def get_document_assignment_slots():
    """"Return a list of all valid assignment slots for documents.

    Currently this is limited to one slot per possible value of the
    `document_type` field.
    """
    vocabulary_factory = getUtility(
        IVocabularyFactory, name="opengever.document.document_types"
    )
    return [
        document_type_assignment_slot_name(term.value)
        for term in vocabulary_factory(None)
    ]


def document_type_assignment_slot_name(value):
    return u"{}.{}".format(
        DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
        value
    )
