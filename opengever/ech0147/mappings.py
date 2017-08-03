

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
    v: k for k, v in CLASSIFICATION_MAPPING.iteritems()}

PRIVACY_LAYER_MAPPING = {
    u'privacy_layer_no': False,
    u'privacy_layer_yes': True,
}
INV_PRIVACY_LAYER_MAPPING = {
    v: k for k, v in PRIVACY_LAYER_MAPPING.iteritems()}
