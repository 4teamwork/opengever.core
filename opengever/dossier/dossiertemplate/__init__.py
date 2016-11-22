from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate  # keep!
from plone import api


def is_dossier_template_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierTemplateSettings)
