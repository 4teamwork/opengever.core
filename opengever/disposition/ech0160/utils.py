from opengever.base.behaviors.classification import IClassification
from opengever.base.vocabulary import voc_term_title


def set_classification_attributes(binding, obj):
    classification = IClassification(obj)
    binding.klassifizierungskategorie = voc_term_title(
        IClassification['classification'], classification.classification)
    binding.datenschutz = (
        True if classification.privacy_layer == 'privacy_layer_yes' else False)
    binding.oeffentlichkeitsstatus = voc_term_title(
        IClassification['public_trial'], classification.public_trial)
    binding.oeffentlichkeitsstatusBegruendung = (
        classification.public_trial_statement)
