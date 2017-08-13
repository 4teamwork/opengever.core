from opengever.base.behaviors.classification import PUBLIC_TRIAL_LIMITED_PUBLIC
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PUBLIC
from opengever.base.behaviors.classification import PUBLIC_TRIAL_UNCHECKED


DOSSIER_STATUS_MAPPING = {
    u'dossier-state-active': u'in_process',
    u'dossier-state-archived': u'archived',
    u'dossier-state-inactive': u'canceled',
    u'dossier-state-resolved': u'closed',
    u'dossier-state-offered': u'in_selection',
}
INV_DOSSIER_STATUS_MAPPING = {
    v: k for k, v in DOSSIER_STATUS_MAPPING.iteritems()}

CLASSIFICATION_MAPPING = {
    u'unprotected': u'unclassified',
    u'confidential': u'confidential',
    u'classified': u'secret',
}
INV_CLASSIFICATION_MAPPING = {
    u'unclassified': u'unprotected',
    u'confidential': u'confidential',
    u'secret': u'classified',
    u'in_house': u'confidential',
}

PRIVACY_LAYER_MAPPING = {
    u'privacy_layer_no': False,
    u'privacy_layer_yes': True,
}
INV_PRIVACY_LAYER_MAPPING = {
    v: k for k, v in PRIVACY_LAYER_MAPPING.iteritems()}

PUBLIC_TRIAL_MAPPING = {
    PUBLIC_TRIAL_LIMITED_PUBLIC: u'not_public',
    PUBLIC_TRIAL_PRIVATE: u'not_public',
    PUBLIC_TRIAL_PUBLIC: u'public',
    PUBLIC_TRIAL_UNCHECKED: u'undefined',
}

INV_PUBLIC_TRIAL_MAPPING = {
    u'not_public': PUBLIC_TRIAL_PRIVATE,
    u'public': PUBLIC_TRIAL_PUBLIC,
    u'undefined': PUBLIC_TRIAL_UNCHECKED,
}
