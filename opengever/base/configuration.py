from AccessControl import getSecurityManager
from AccessControl.users import nobody
from collections import OrderedDict
from opengever.activity.interfaces import IActivitySettings
from opengever.api.user_settings import serialize_setting
from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import get_gever_portal_url
from opengever.base.interfaces import IFavoritesSettings
from opengever.base.interfaces import IGeverSettings
from opengever.base.interfaces import IGeverUI
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.interfaces import ISearchSettings
from opengever.base.interfaces import IUserSnapSettings
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.contact.interfaces import IContactSettings
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.interfaces import IFTPSTransportSettings
from opengever.document.interfaces import IDocumentSettings
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.meeting.interfaces import IMeetingSettings
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.ogds.models.user_settings import UserSettings
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.sharing.interfaces import ISharingConfiguration
from opengever.task.interfaces import ITaskSettings
from opengever.workspace.interfaces import IWorkspaceSettings
from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from pkg_resources import get_distribution
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
import os


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
        config['portal_url'] = get_gever_portal_url()
        config['cas_url'] = get_cas_server_url()
        config['apps_url'] = os.environ.get('APPS_ENDPOINT_URL')
        return config

    def get_info(self):
        info = OrderedDict()
        info['@id'] = self.context.absolute_url() + '/@config'
        info['version'] = get_distribution('opengever.core').version
        user = api.user.get_current()
        if user.getId():
            info['userid'] = user.getId()
            info['user_fullname'] = user.getProperty('fullname')
            info['user_email'] = user.getProperty('email')
        return info

    def get_user_settings(self):
        setting = UserSettings.query.filter_by(userid=api.user.get_current().id).one_or_none()
        return serialize_setting(setting)

    def get_settings(self):
        settings = OrderedDict()
        settings['max_dossier_levels'] = api.portal.get_registry_record('maximum_dossier_depth', interface=IDossierContainerTypes) + 1  # noqa
        settings['max_repositoryfolder_levels'] = api.portal.get_registry_record('maximum_repository_depth', interface=IRepositoryFolderRecords)  # noqa
        settings['recently_touched_limit'] = api.portal.get_registry_record('limit', interface=IRecentlyTouchedSettings)  # noqa
        settings['document_preserved_as_paper_default'] = api.portal.get_registry_record('preserved_as_paper_default', interface=IDocumentSettings)  # noqa
        settings['usersnap_api_key'] = api.portal.get_registry_record('api_key', interface=IUserSnapSettings)  # noqa
        settings['nightly_jobs'] = self.get_nightly_jobs_settings()
        settings['oneoffixx_settings'] = self.get_oneoffixx_settings()
        settings['user_settings'] = self.get_user_settings()
        settings['sharing_configuration'] = self.get_sharing_configuration()
        return settings

    def get_nightly_jobs_settings(self):
        nightly_jobs_settings = {}
        nightly_jobs_settings['start_time'] = str(api.portal.get_registry_record('start_time', interface=INightlyJobsSettings))  # noqa
        nightly_jobs_settings['end_time'] = str(api.portal.get_registry_record('end_time', interface=INightlyJobsSettings))  # noqa
        return nightly_jobs_settings

    def get_sharing_configuration(self):
        sharing_configuration = OrderedDict()
        sharing_configuration['white_list_prefix'] = api.portal.get_registry_record('white_list_prefix', interface=ISharingConfiguration)  # noqa
        sharing_configuration['black_list_prefix'] = api.portal.get_registry_record('black_list_prefix', interface=ISharingConfiguration)  # noqa
        return sharing_configuration

    def get_oneoffixx_settings(self):
        oneoffixx_settings = OrderedDict()
        oneoffixx_settings['fake_sid'] = api.portal.get_registry_record('fake_sid', interface=IOneoffixxSettings)
        oneoffixx_settings['double_encode_bug'] = api.portal.get_registry_record('double_encode_bug', interface=IOneoffixxSettings)  # noqa
        oneoffixx_settings['cache_timeout'] = api.portal.get_registry_record('cache_timeout', interface=IOneoffixxSettings)
        oneoffixx_settings['scope'] = api.portal.get_registry_record('scope', interface=IOneoffixxSettings)
        return oneoffixx_settings

    def get_features(self):
        features = OrderedDict()
        features['activity'] = api.portal.get_registry_record('is_feature_enabled', interface=IActivitySettings)
        features['archival_file_conversion'] = api.portal.get_registry_record('archival_file_conversion_enabled', interface=IDossierResolveProperties)  # noqa
        features['archival_file_conversion_blacklist'] = api.portal.get_registry_record('archival_file_conversion_blacklist', interface=IDossierResolveProperties)  # noqa
        features['changed_for_end_date'] = api.portal.get_registry_record('use_changed_for_end_date', interface=IDossierResolveProperties)  # noqa
        features['contacts'] = api.portal.get_registry_record('is_feature_enabled', interface=IContactSettings)
        features['disposition_transport_filesystem'] = api.portal.get_registry_record('enabled', interface=IFilesystemTransportSettings)  # noqa
        features['disposition_transport_ftps'] = api.portal.get_registry_record('enabled', interface=IFTPSTransportSettings)  # noqa
        features['doc_properties'] = api.portal.get_registry_record('create_doc_properties', interface=ITemplateFolderProperties)  # noqa
        features['dossier_templates'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierTemplateSettings)  # noqa
        features['ech0147_export'] = api.portal.get_registry_record('ech0147_export_enabled', interface=IECH0147Settings)
        features['ech0147_import'] = api.portal.get_registry_record('ech0147_import_enabled', interface=IECH0147Settings)
        features['favorites'] = api.portal.get_registry_record('is_feature_enabled', interface=IFavoritesSettings)
        features['gever_ui_enabled'] = api.portal.get_registry_record('is_feature_enabled', interface=IGeverUI)
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
        features['workspace_client'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceClientSettings)  # noqa
        features['private_tasks'] = api.portal.get_registry_record('private_task_feature_enabled', interface=ITaskSettings)
        features['optional_task_permissions_revoking'] = api.portal.get_registry_record('optional_task_permissions_revoking_enabled', interface=ITaskSettings)  # noqa
        return features
