from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from plone import api


def is_dossier_template_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierTemplateSettings)
