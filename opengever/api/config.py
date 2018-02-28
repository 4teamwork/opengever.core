from opengever.activity.interfaces import IActivitySettings
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
from plone.restapi.services import Service


class Config(Service):
    """GEVER configuration"""

    def reply(self):
        config = {}

        config['@id'] = api.portal.get().absolute_url() + '/@config'

        config['max_repositoryfolder_levels'] = api.portal.get_registry_record(
            'maximum_repository_depth', interface=IRepositoryFolderRecords)

        config['max_dossier_levels'] = api.portal.get_registry_record(
            'maximum_dossier_depth', interface=IDossierContainerTypes) + 1

        config['features'] = {}

        config['features']['activity'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IActivitySettings)
        config['features']['contacts'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IContactSettings)
        config['features']['doc_properties'] = api.portal.get_registry_record(
            'create_doc_properties', interface=ITemplateFolderProperties)
        config['features']['dossier_templates'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IDossierTemplateSettings)
        config['features']['ech0147_export'] = api.portal.get_registry_record(
            'ech0147_export_enabled', interface=IECH0147Settings)
        config['features']['ech0147_import'] = api.portal.get_registry_record(
            'ech0147_import_enabled', interface=IECH0147Settings)
        config['features']['meetings'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IMeetingSettings)
        config['features']['officeatwork'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IOfficeatworkSettings)
        config['features']['officeconnector_attach'] = api.portal.get_registry_record(
            'attach_to_outlook_enabled', interface=IOfficeConnectorSettings)
        config['features']['officeconnector_checkout'] = api.portal.get_registry_record(
            'direct_checkout_and_edit_enabled', interface=IOfficeConnectorSettings)
        config['features']['preview'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IGeverBumblebeeSettings)
        config['features']['preview_open_pdf_in_new_window'] = api.portal.get_registry_record(
            'open_pdf_in_a_new_window', interface=IGeverBumblebeeSettings)
        config['features']['repositoryfolder_documents_tab'] = api.portal.get_registry_record(
            'show_documents_tab', interface=IRepositoryFolderRecords)
        config['features']['repositoryfolder_tasks_tab'] = api.portal.get_registry_record(
            'show_tasks_tab', interface=IRepositoryFolderRecords)
        config['features']['word_meetings'] = api.portal.get_registry_record(
            'is_word_implementation_enabled', interface=IMeetingSettings)
        config['features']['workspace'] = api.portal.get_registry_record(
            'is_feature_enabled', interface=IWorkspaceSettings)
        config['features']['solr'] = api.portal.get_registry_record(
            'use_solr', interface=ISearchSettings)

        return config
