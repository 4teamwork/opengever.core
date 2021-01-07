from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class PropertySheetAssignmentVocabulary(object):
    """Return valid property sheet assignments."""

    def __call__(self, context):
        vocabulary_factory = getUtility(
            IVocabularyFactory, name="opengever.document.document_types"
        )
        document_types_vocabulary = vocabulary_factory(context)

        assignment_terms = []
        for term in document_types_vocabulary:
            name = u"IDocumentMetadata.document_type.{}".format(
                term.value
            )
            assignment_terms.append(SimpleTerm(name))

        return SimpleVocabulary(assignment_terms)
