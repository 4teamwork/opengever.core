from opengever.base.behaviors.classification import IClassification
from opengever.base.vocabulary import voc_term_title
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
