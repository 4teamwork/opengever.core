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


def _get_document_type_slots():
    vocabulary_factory = getUtility(
        IVocabularyFactory, name="opengever.document.document_types"
    )
    return [
        document_type_assignment_slot_name(term.value)
        for term in vocabulary_factory(None)
    ]


def get_document_assignment_slots():
    """"Return a list of all valid assignment slots for documents.

    This is limited to one slot per possible value of the
    `document_type` field and the default document slot.
    """

    return [DOCUMENT_DEFAULT_ASSIGNMENT_SLOT] + _get_document_type_slots()


def document_type_assignment_slot_name(value):
    return u"{}.{}".format(
        DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
        value
    )


def _get_dossier_type_slots():
    vocabulary_factory = getUtility(
        IVocabularyFactory, name="opengever.dossier.dossier_types"
    )
    return [
        dossier_type_assignment_slot_name(term.value)
        for term in vocabulary_factory(None)
    ]


def get_dossier_assignment_slots():
    """"Return a list of all valid assignment slots for dossiers.

    This is limited to one slot per possible value of the
    `dossier_type` field and the default dossier slot.
    """

    return [DOSSIER_DEFAULT_ASSIGNMENT_SLOT] + _get_dossier_type_slots()


def dossier_type_assignment_slot_name(value):
    return u"{}.{}".format(DOSSIER_TYPE_ASSIGNMENT_SLOT_PREFIX, value)


def get_slots_enforcing_unique_field_names(slot_name):
    """Return other slots that enforce unique fields names.

    Given a slot name return all other slot names which cannot have field
    names overlap with this slot.

    This function is used by storage to validate if new property sheets can
    be added.
    """
    if slot_name == DOCUMENT_DEFAULT_ASSIGNMENT_SLOT:
        return set(_get_document_type_slots())
    elif slot_name == DOSSIER_DEFAULT_ASSIGNMENT_SLOT:
        return set(_get_dossier_type_slots())
    elif slot_name.startswith(DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX):
        return {DOCUMENT_DEFAULT_ASSIGNMENT_SLOT}
    elif slot_name.startswith(DOSSIER_TYPE_ASSIGNMENT_SLOT_PREFIX):
        return {DOSSIER_DEFAULT_ASSIGNMENT_SLOT}

    return {}
