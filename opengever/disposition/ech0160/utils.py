from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from opengever.base.behaviors.classification import IClassification
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


def set_classification_attributes(binding, obj):
    classification = IClassification(obj)
    binding.klassifizierungskategorie = voc_term_title(
        IClassification['classification'], classification.classification)
    binding.datenschutz = (True if classification.privacy_layer ==
                           'privacy_layer_yes' else False)
    binding.oeffentlichkeitsstatus = voc_term_title(
        IClassification['public_trial'], classification.public_trial)
    binding.oeffentlichkeitsstatusBegruendung = (
        classification.public_trial_statement)
