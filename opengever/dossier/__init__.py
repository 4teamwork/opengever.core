from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.dossier")


def is_dossier_checklist_feature_enabled():
    # Avoid circular imports
    from opengever.dossier.interfaces import IDossierChecklistSettings
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierChecklistSettings)
