from .action_info import PatchActionInfo
from .cmf_catalog_aware import PatchCMFCatalogAware
from .cmf_catalog_aware import PatchCMFCatalogAwareHandlers
from .content_history_viewlet import PatchFullHistory
from .default_values import PatchBuilderCreate
from .default_values import PatchDexterityContentGetattr
from .default_values import PatchDexterityDefaultAddForm
from .default_values import PatchDXCreateContentInContainer
from .default_values import PatchInvokeFactory
from .default_values import PatchTransmogrifyDXSchemaUpdater
from .default_values import PatchZ3CFormChangedField
from .default_values import PatchZ3CFormWidgetUpdate
from .development import PatchBaseOrderedViewletManagerExceptions
from .exception_formatter import PatchExceptionFormatter
from .extendedpathindex import PatchExtendedPathIndex
from .filter_trashed_from_catalog import PatchCatalogToFilterTrashedDocs
from .history_handler_tool import PatchCMFEditonsHistoryHandlerTool
from .jsonschema_for_portal_type import PatchGetJsonschemaForPortalType
from .language_tool import PatchLanguageToolCall
from .maybe_report_exception import PatchMaybeReportException
from .namedfile_data_converter import PatchNamedfileNamedDataConverter
from .paste_permission import PatchDXContainerPastePermission
from .plone_43rc1_upgrade import PatchPlone43RC1Upgrade
from .readonly import PatchCASAuthSetLoginTimes
from .readonly import PatchCheckPermission
from .readonly import PatchContentRulesHandlerOnLogin
from .readonly import PatchMembershipToolCreateMemberarea
from .readonly import PatchMembershipToolSetLoginTimes
from .readonly import PatchPloneProtectOnUserLogsIn
from .readonly import PatchPloneUserAllowed
from .readonly import PatchPloneUserGetRolesInContext
from .relation_fields import PatchRelationFieldEventHandlers
from .resource_registries_url_regex import PatchResourceRegistriesURLRegex
from .restapi_utils import PatchRestAPICreateForm
from .rolemanager import PatchOFSRoleManager
from .scrub_bobo_exceptions import ScrubBoboExceptions
from .session import PatchSessionCookie
from .site_error_log import PatchSiteErrorLog
from .tus_upload import PatchTUSUploadCleanup
from .tz_for_log import PatchZ2LogTimezone
from .verify_object_paste import PatchCopyContainerVerifyObjectPaste
from .webdav_lock_timeout import PatchWebDAVLockTimeout
from .workflowtool import PatchWorkflowTool
from opengever.debug import debug_modified_out_of_sync_env_var_is_set
from opengever.debug.patches.modified_out_of_sync import PatchConnectionRegister
from opengever.readonly import readonly_env_var_is_set


PatchSiteErrorLog()()
PatchActionInfo()()
PatchBaseOrderedViewletManagerExceptions()()
PatchBuilderCreate()()
PatchCASAuthSetLoginTimes()()
PatchCatalogToFilterTrashedDocs()()
PatchCMFCatalogAware()()
PatchCMFCatalogAwareHandlers()()
PatchCMFEditonsHistoryHandlerTool()()
PatchContentRulesHandlerOnLogin()()
PatchCopyContainerVerifyObjectPaste()()
PatchDexterityContentGetattr()()
PatchDexterityDefaultAddForm()()
PatchDXContainerPastePermission()()
PatchDXCreateContentInContainer()()
PatchExceptionFormatter()()
PatchExtendedPathIndex()()
PatchFullHistory()()
PatchGetJsonschemaForPortalType()()
PatchInvokeFactory()()
PatchLanguageToolCall()()
PatchMaybeReportException()()
PatchMembershipToolCreateMemberarea()()
PatchMembershipToolSetLoginTimes()()
PatchNamedfileNamedDataConverter()()
PatchOFSRoleManager()()
PatchPlone43RC1Upgrade()()
PatchPloneProtectOnUserLogsIn()()
PatchRelationFieldEventHandlers()()
PatchRestAPICreateForm()()
PatchResourceRegistriesURLRegex()()
PatchSessionCookie()()
PatchTransmogrifyDXSchemaUpdater()()
PatchTUSUploadCleanup()()
PatchWebDAVLockTimeout()()
PatchWorkflowTool()()
PatchZ2LogTimezone()()
PatchZ3CFormChangedField()()
PatchZ3CFormWidgetUpdate()()
ScrubBoboExceptions()()

# These three patches implement role and permission filtering during RO mode.
# We only apply these conditionally when RO mode actually is active.
if readonly_env_var_is_set():
    PatchCheckPermission()()
    PatchPloneUserAllowed()()
    PatchPloneUserGetRolesInContext()()

# This patch helps debugging an issue where modified of objects is out of date
# with modified in the catalog.
if debug_modified_out_of_sync_env_var_is_set():
    PatchConnectionRegister()()
