from collections import OrderedDict
from opengever.activity.interfaces import IActivitySettings
from opengever.base.interfaces import IFavoritesSettings
from opengever.base.interfaces import IGeverSettings
from opengever.base.interfaces import ISearchSettings
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.contact.interfaces import IContactSettings
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.meeting.interfaces import IMeetingSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.workspace.interfaces import IWorkspaceSettings
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import adapter
from zope.interface import implementer


@implementer(IGeverSettings)
@adapter(ISiteRoot)
class GeverSettingsAdpaterV1(object):
    """Returns the current site configuration in the API v1 format."""

    def __init__(self, context):
        super(GeverSettingsAdpaterV1, self).__init__()
        self.context = context

    def get_config(self):
        config = self.get_info()
        config.update(self.get_settings())
        config['features'] = self.get_features()
        return config

    def get_info(self):
        info = OrderedDict()
        info['@id'] = self.context.absolute_url() + '/@config'
        return info

    def get_settings(self):
        settings = OrderedDict()
        settings['max_dossier_levels'] = api.portal.get_registry_record('maximum_dossier_depth', interface=IDossierContainerTypes) + 1  # noqa
        settings['max_repositoryfolder_levels'] = api.portal.get_registry_record('maximum_repository_depth', interface=IRepositoryFolderRecords)  # noqa
        return settings

    def get_features(self):
        features = OrderedDict()
        features['activity'] = api.portal.get_registry_record('is_feature_enabled', interface=IActivitySettings)
        features['contacts'] = api.portal.get_registry_record('is_feature_enabled', interface=IContactSettings)
        features['doc_properties'] = api.portal.get_registry_record('create_doc_properties', interface=ITemplateFolderProperties)  # noqa
        features['dossier_templates'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierTemplateSettings)  # noqa
        features['ech0147_export'] = api.portal.get_registry_record('ech0147_export_enabled', interface=IECH0147Settings)
        features['ech0147_import'] = api.portal.get_registry_record('ech0147_import_enabled', interface=IECH0147Settings)
        features['favorites'] = api.portal.get_registry_record('is_feature_enabled', interface=IFavoritesSettings)
        features['meetings'] = api.portal.get_registry_record('is_feature_enabled', interface=IMeetingSettings)
        features['officeatwork'] = api.portal.get_registry_record('is_feature_enabled', interface=IOfficeatworkSettings)
        features['officeconnector_attach'] = api.portal.get_registry_record('attach_to_outlook_enabled', interface=IOfficeConnectorSettings)  # noqa
        features['officeconnector_checkout'] = api.portal.get_registry_record('direct_checkout_and_edit_enabled', interface=IOfficeConnectorSettings)  # noqa
        features['preview_auto_refresh'] = api.portal.get_registry_record('is_auto_refresh_enabled', interface=IGeverBumblebeeSettings)  # noqa
        features['preview_open_pdf_in_new_window'] = api.portal.get_registry_record('open_pdf_in_a_new_window', interface=IGeverBumblebeeSettings)  # noqa
        features['preview'] = api.portal.get_registry_record('is_feature_enabled', interface=IGeverBumblebeeSettings)
        features['repositoryfolder_documents_tab'] = api.portal.get_registry_record('show_documents_tab', interface=IRepositoryFolderRecords)  # noqa
        features['repositoryfolder_tasks_tab'] = api.portal.get_registry_record('show_tasks_tab', interface=IRepositoryFolderRecords)  # noqa
        features['solr'] = api.portal.get_registry_record('use_solr', interface=ISearchSettings)
        features['word_meetings'] = api.portal.get_registry_record('is_word_implementation_enabled', interface=IMeetingSettings)  # noqa
        features['workspace'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceSettings)
        return features
