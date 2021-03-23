from opengever.propertysheets.assignment import DOCUMENT_DEFAULT_ASSIGNMENT_SLOT


def fixture_assignment_factory():
    return [
        DOCUMENT_DEFAULT_ASSIGNMENT_SLOT,
        u"IDocumentMetadata.document_type.contract",
        u"IDocumentMetadata.document_type.question",
    ]
