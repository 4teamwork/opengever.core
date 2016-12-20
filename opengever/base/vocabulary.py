from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


def voc_term_title(field, value):
    """Returns the vocabulary term title for the given field and value.
    """

    if value is None:
        return None
    factory = None
    if field.vocabulary:
        factory = field.vocabulary
    elif field.vocabularyName:
        factory = getUtility(IVocabularyFactory, name=field.vocabularyName)
    if factory is not None:
        voc = factory(None)
        return voc.getTerm(value).title
    return value
