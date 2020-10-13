from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from plone import api


def is_dossier_template_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IDossierTemplateSettings)


def is_create_dossier_from_template_available(context):
    return is_dossier_template_feature_enabled() and context.is_leaf_node() and \
            api.user.has_permission('opengever.dossier: Add businesscasedossier', obj=context) and \
            (context.allow_add_businesscase_dossier or context.addable_dossier_templates)
