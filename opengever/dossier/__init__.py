from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.dossier")


def is_dossier_checklist_feature_enabled():
    # Avoid circular imports
    from opengever.dossier.interfaces import IDossierChecklistSettings
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierChecklistSettings)


def is_grant_role_manager_to_responsible_enabled():
    # Avoid circular imports
    from opengever.dossier.interfaces import IDossierSettings
    return api.portal.get_registry_record(
        'grant_role_manager_to_responsible', interface=IDossierSettings)


def is_grant_dossier_manager_to_responsible_enabled():
    # Avoid circular imports
    from opengever.dossier.interfaces import IDossierSettings
    return api.portal.get_registry_record(
        'grant_dossier_manager_to_responsible', interface=IDossierSettings)
