from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import hashlib


def file_checksum(filename, chunksize=65536):
    """Calculates a checksum for the given file."""
    h = hashlib.md5()
    with open(filename, 'rb') as f:
        chunk = f.read(chunksize)
        while len(chunk) > 0:
            h.update(chunk)
            chunk = f.read(chunksize)
        return u'MD5', h.hexdigest()


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
