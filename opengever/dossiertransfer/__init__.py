import plone.api


def is_dossier_transfer_feature_enabled():
    # Avoid circular imports
    from opengever.dossiertransfer.interfaces import IDossierTransferSettings

    return plone.api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierTransferSettings)
