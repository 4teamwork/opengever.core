from AccessControl import getSecurityManager
from AccessControl.users import nobody
from collections import OrderedDict
from opengever.activity.interfaces import IActivitySettings
from opengever.base.casauth import get_cas_server_url
from opengever.base.interfaces import IFavoritesSettings
from opengever.base.interfaces import IGeverSettings
from opengever.base.interfaces import IGeverUI
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.interfaces import ISearchSettings
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.contact.interfaces import IContactSettings
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.meeting.interfaces import IMeetingSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.task.interfaces import ITaskSettings
from opengever.workspace.interfaces import IWorkspaceSettings
from pkg_resources import get_distribution
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IGeverSettings)
@adapter(Interface)
class GeverSettingsAdpaterV1(object):
    """Returns the current site configuration in the API v1 format."""

    def __init__(self, context):
        super(GeverSettingsAdpaterV1, self).__init__()
        self.context = context

    def get_config(self):
        config = self.get_info()
        # Only expose essential configuration for unauthenticated requests
        if getSecurityManager().getUser() != nobody:
            config.update(self.get_settings())
            config['features'] = self.get_features()
        config['root_url'] = api.portal.get().absolute_url()
        config['cas_url'] = get_cas_server_url()
        return config

    def get_info(self):
        info = OrderedDict()
        info['@id'] = self.context.absolute_url() + '/@config'
        info['version'] = get_distribution('opengever.core').version
        return info

    def get_settings(self):
        settings = OrderedDict()
        settings['max_dossier_levels'] = api.portal.get_registry_record('maximum_dossier_depth', interface=IDossierContainerTypes) + 1  # noqa
        settings['max_repositoryfolder_levels'] = api.portal.get_registry_record('maximum_repository_depth', interface=IRepositoryFolderRecords)  # noqa
        settings['recently_touched_limit'] = api.portal.get_registry_record('limit', interface=IRecentlyTouchedSettings)  # noqa
        settings['oneoffixx_settings'] = self.get_oneoffixx_settings()
        return settings

    def get_oneoffixx_settings(self):
        oneoffixx_settings = OrderedDict()
        oneoffixx_settings['baseurl'] = api.portal.get_registry_record('baseurl', interface=IOneoffixxSettings)
        oneoffixx_settings['fake_sid'] = api.portal.get_registry_record('fake_sid', interface=IOneoffixxSettings)
        oneoffixx_settings['double_encode_bug'] = api.portal.get_registry_record('double_encode_bug', interface=IOneoffixxSettings)  # noqa
        return oneoffixx_settings

    def get_features(self):
        features = OrderedDict()
        features['activity'] = api.portal.get_registry_record('is_feature_enabled', interface=IActivitySettings)
        features['archival_file_conversion'] = api.portal.get_registry_record('archival_file_conversion_enabled', interface=IDossierResolveProperties)  # noqa
        features['contacts'] = api.portal.get_registry_record('is_feature_enabled', interface=IContactSettings)
        features['doc_properties'] = api.portal.get_registry_record('create_doc_properties', interface=ITemplateFolderProperties)  # noqa
        features['dossier_templates'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierTemplateSettings)  # noqa
        features['ech0147_export'] = api.portal.get_registry_record('ech0147_export_enabled', interface=IECH0147Settings)
        features['ech0147_import'] = api.portal.get_registry_record('ech0147_import_enabled', interface=IECH0147Settings)
        features['favorites'] = api.portal.get_registry_record('is_feature_enabled', interface=IFavoritesSettings)
        features['gever_ui_enabled'] = api.portal.get_registry_record('is_feature_enabled', interface=IGeverUI)
        features['gever_ui_path'] = api.portal.get_registry_record('path', interface=IGeverUI)
        features['journal_pdf'] = api.portal.get_registry_record('journal_pdf_enabled', interface=IDossierResolveProperties)
        features['tasks_pdf'] = api.portal.get_registry_record('tasks_pdf_enabled', interface=IDossierResolveProperties)
        features['meetings'] = api.portal.get_registry_record('is_feature_enabled', interface=IMeetingSettings)
        features['officeatwork'] = api.portal.get_registry_record('is_feature_enabled', interface=IOfficeatworkSettings)
        features['officeconnector_attach'] = api.portal.get_registry_record('attach_to_outlook_enabled', interface=IOfficeConnectorSettings)  # noqa
        features['officeconnector_checkout'] = api.portal.get_registry_record('direct_checkout_and_edit_enabled', interface=IOfficeConnectorSettings)  # noqa
        features['oneoffixx'] = api.portal.get_registry_record('is_feature_enabled', interface=IOneoffixxSettings)
        features['preview_auto_refresh'] = api.portal.get_registry_record('is_auto_refresh_enabled', interface=IGeverBumblebeeSettings)  # noqa
        features['preview_open_pdf_in_new_window'] = api.portal.get_registry_record('open_pdf_in_a_new_window', interface=IGeverBumblebeeSettings)  # noqa
        features['preview'] = api.portal.get_registry_record('is_feature_enabled', interface=IGeverBumblebeeSettings)
        features['purge_trash'] = api.portal.get_registry_record('purge_trash_enabled', interface=IDossierResolveProperties)
        features['repositoryfolder_documents_tab'] = api.portal.get_registry_record('show_documents_tab', interface=IRepositoryFolderRecords)  # noqa
        features['repositoryfolder_proposals_tab'] = api.portal.get_registry_record('show_proposals_tab', interface=IRepositoryFolderRecords)  # noqa
        features['repositoryfolder_tasks_tab'] = api.portal.get_registry_record('show_tasks_tab', interface=IRepositoryFolderRecords)  # noqa
        features['resolver_name'] = api.portal.get_registry_record('resolver_name', interface=IDossierResolveProperties)
        features['sablon_date_format'] = api.portal.get_registry_record('sablon_date_format_string', interface=IMeetingSettings)  # noqa
        features['solr'] = api.portal.get_registry_record('use_solr', interface=ISearchSettings)
        features['workspace'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceSettings)
        features['private_tasks'] = api.portal.get_registry_record('private_task_feature_enabled', interface=ITaskSettings)
        return features
