from AccessControl import getSecurityManager
from AccessControl.users import nobody
from collections import OrderedDict
from ftw import bumblebee
from opengever.activity.interfaces import IActivitySettings
from opengever.api.user_settings import serialize_setting
from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import get_gever_portal_url
from opengever.base.interfaces import IFavoritesSettings
from opengever.base.interfaces import IGeverSettings
from opengever.base.interfaces import IGeverUI
from opengever.base.interfaces import IHubSpotSettings
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.interfaces import ISearchSettings
from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from opengever.disposition.interfaces import IDispositionSettings
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.interfaces import IFTPSTransportSettings
from opengever.document.interfaces import IDocumentSettings
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.filing.interfaces import IFilingNumberActivatedLayer
from opengever.dossier.interfaces import IDossierChecklistSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.interfaces import IDossierSettings
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.dossier.vocabularies import count_available_dossier_types
from opengever.dossiertransfer.interfaces import IDossierTransferSettings
from opengever.ech0147.interfaces import IECH0147Settings
from opengever.kub import is_kub_feature_enabled
from opengever.mail.interfaces import IMailDownloadSettings
from opengever.meeting.interfaces import IMeetingSettings
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from opengever.officeatwork.interfaces import IOfficeatworkSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.user_settings import UserSettings
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.readonly import is_in_readonly_mode
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.ris.interfaces import IRisSettings
from opengever.sharing.interfaces import ISharingConfiguration
from opengever.task.interfaces import ITaskSettings
from opengever.tasktemplates.interfaces import ITaskTemplateSettings
from opengever.workspace import is_invitation_feature_enabled
from opengever.workspace.interfaces import IToDoSettings
from opengever.workspace.interfaces import IWorkspaceMeetingSettings
from opengever.workspace.interfaces import IWorkspaceSettings
from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from pkg_resources import get_distribution
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
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
        config['application_type'] = self.get_application_type()
        config['bumblebee_notifications_url'] = bumblebee.get_service_v3().get_notifications_url()
        config['ris_base_url'] = self.get_ris_base_url()
        config['is_readonly'] = is_in_readonly_mode()
        return config

    def get_info(self):
        info = OrderedDict()
        info['@id'] = self.context.absolute_url() + '/@config'
        info['version'] = get_distribution('opengever.core').version
        info['admin_unit'] = get_current_admin_unit().id()
        info['org_unit'] = get_current_org_unit().id()

        user = api.user.get_current()
        if user.getId():
            serializer = queryMultiAdapter((user, getRequest()), ISerializeToJson)
            info['current_user'] = OrderedDict(serializer())
        return info

    def get_application_type(self):
        if api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceSettings):
            return 'teamraum'
        return 'gever'

    def get_ris_base_url(self):
        ris_base_url = api.portal.get_registry_record(name='base_url', interface=IRisSettings)
        if ris_base_url:
            return ris_base_url.rstrip("/")
        return ''

    def get_user_settings(self):
        setting = UserSettings.query.filter_by(userid=api.user.get_current().id).one_or_none()
        return serialize_setting(setting)

    def get_settings(self):
        settings = OrderedDict()
        settings['max_dossier_levels'] = api.portal.get_registry_record('maximum_dossier_depth', interface=IDossierContainerTypes) + 1  # noqa
        settings['max_repositoryfolder_levels'] = api.portal.get_registry_record('maximum_repository_depth', interface=IRepositoryFolderRecords)  # noqa
        settings['recently_touched_limit'] = api.portal.get_registry_record('limit', interface=IRecentlyTouchedSettings)  # noqa
        settings['document_preserved_as_paper_default'] = api.portal.get_registry_record('preserved_as_paper_default', interface=IDocumentSettings)  # noqa
        settings['nightly_jobs'] = self.get_nightly_jobs_settings()
        settings['user_settings'] = self.get_user_settings()
        settings['sharing_configuration'] = self.get_sharing_configuration()
        settings['p7m_extension_replacement'] = api.portal.get_registry_record('p7m_extension_replacement', interface=IMailDownloadSettings)  # noqa
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

    def get_features(self):
        features = OrderedDict()
        features['activity'] = api.portal.get_registry_record('is_feature_enabled', interface=IActivitySettings)
        features['archival_file_conversion'] = api.portal.get_registry_record('archival_file_conversion_enabled', interface=IDossierResolveProperties)  # noqa
        features['archival_file_conversion_blacklist'] = api.portal.get_registry_record('archival_file_conversion_blacklist', interface=IDossierResolveProperties)  # noqa
        features['changed_for_end_date'] = api.portal.get_registry_record('use_changed_for_end_date', interface=IDossierResolveProperties)  # noqa
        features['classic_ui_enabled'] = api.portal.get_registry_record('is_classic_ui_enabled', interface=IGeverUI)
        features['contacts'] = self._get_contact_type()
        features['disposition_disregard_retention_period'] = api.portal.get_registry_record('disregard_retention_period', interface=IDispositionSettings)  # noqa
        features['disposition_transport_filesystem'] = api.portal.get_registry_record('enabled', interface=IFilesystemTransportSettings)  # noqa
        features['disposition_transport_ftps'] = api.portal.get_registry_record('enabled', interface=IFTPSTransportSettings)  # noqa
        features['doc_properties'] = api.portal.get_registry_record('create_doc_properties', interface=ITemplateFolderProperties)  # noqa
        features['dossier_checklist'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierChecklistSettings)  # noqa
        features['dossier_templates'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierTemplateSettings)  # noqa
        features['dossier_transfers'] = api.portal.get_registry_record('is_feature_enabled', interface=IDossierTransferSettings)  # noqa
        features['ech0147_export'] = api.portal.get_registry_record('ech0147_export_enabled', interface=IECH0147Settings)
        features['ech0147_import'] = api.portal.get_registry_record('ech0147_import_enabled', interface=IECH0147Settings)
        features['favorites'] = api.portal.get_registry_record('is_feature_enabled', interface=IFavoritesSettings)
        features['filing_number'] = self.is_filing_number_feature_installed()
        features['gever_ui_enabled'] = api.portal.get_registry_record('is_feature_enabled', interface=IGeverUI)
        features['grant_role_manager_to_responsible'] = api.portal.get_registry_record('grant_role_manager_to_responsible', interface=IDossierSettings)  # noqa
        features['hubspot'] = api.portal.get_registry_record('is_feature_enabled', interface=IHubSpotSettings)  # noqa
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
        features['tasktemplatefolder_nesting'] = api.portal.get_registry_record('is_tasktemplatefolder_nesting_enabled', interface=ITaskTemplateSettings)  # noqa
        features['workspace'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceSettings)
        features['workspace_invitation'] = is_invitation_feature_enabled()
        features['workspace_client'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceClientSettings)  # noqa
        features['workspace_creation_restricted'] = api.portal.get_registry_record(
            'is_creation_restricted', interface=IWorkspaceSettings)
        features['workspace_meetings'] = api.portal.get_registry_record('is_feature_enabled', interface=IWorkspaceMeetingSettings)  # noqa
        features['workspace_todo'] = api.portal.get_registry_record('is_feature_enabled', interface=IToDoSettings)
        features['private_tasks'] = api.portal.get_registry_record('private_task_feature_enabled', interface=ITaskSettings)
        features['optional_task_permissions_revoking'] = api.portal.get_registry_record('optional_task_permissions_revoking_enabled', interface=ITaskSettings)  # noqa
        features['multiple_dossier_types'] = count_available_dossier_types() > 1

        return features

    def is_filing_number_feature_installed(self):
        return IFilingNumberActivatedLayer.providedBy(getRequest())

    def _get_contact_type(self):
        if is_kub_feature_enabled():
            return "kub"
        return "plone"
