from collective import elephantvocabulary
from collective.elephantvocabulary.interfaces import IElephantVocabulary
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implements
from zope.schema.interfaces import IIterableSource
from zope.schema.interfaces import ISource
from zope.schema.interfaces import IVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IVocabularyTokenized


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


class WrapperBase(elephantvocabulary.WrapperBase):
    """This is a customized elephant vocabulary wrapper class which
    provides the IVocabularyTokenized interfaces if the
    underlying vocabulary provides it.

    This ensures that a field providing an elephant vocabulary is serialized properly.
    """
    implements(IElephantVocabulary, IVocabulary, ISource, IIterableSource)

    def __init__(self, vocab, *args, **kwargs):
        super(WrapperBase, self).__init__(vocab, *args, **kwargs)
        if IVocabularyTokenized.providedBy(vocab):
            alsoProvides(self, IVocabularyTokenized)


def wrap_vocabulary(*args, **kwargs):
    """Customized elephant vocaubulary wrapper function which replaces the
    default wrapper_class with our own WrapperBase class.
    """
    if 'wrapper_class' not in kwargs:
        kwargs['wrapper_class'] = WrapperBase
    return elephantvocabulary.VocabularyFactory(*args, **kwargs)
