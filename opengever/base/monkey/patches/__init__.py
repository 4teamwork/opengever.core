from .action_info import PatchActionInfo
from .cmf_catalog_aware import PatchCMFCatalogAware
from .cmf_catalog_aware import PatchCMFCatalogAwareHandlers
from .default_values import PatchBuilderCreate
from .default_values import PatchDeserializeFromJson
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
from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
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
from .resource_registries_url_regex import PatchResourceRegistriesURLRegex
from .rolemanager import PatchOFSRoleManager
from .scrub_bobo_exceptions import ScrubBoboExceptions
from .tz_for_log import PatchZ2LogTimezone
from .verify_object_paste import PatchCopyContainerVerifyObjectPaste
from .webdav_lock_timeout import PatchWebDAVLockTimeout
from .workflowtool import PatchWorkflowTool


PatchActionInfo()()
PatchBaseOrderedViewletManagerExceptions()()
PatchBuilderCreate()()
PatchCASAuthSetLoginTimes()()
PatchCatalogToFilterTrashedDocs()()
PatchCheckPermission()()
PatchCMFCatalogAware()()
PatchCMFCatalogAwareHandlers()()
PatchCMFEditonsHistoryHandlerTool()()
PatchContentRulesHandlerOnLogin()()
PatchCopyContainerVerifyObjectPaste()()
PatchDeserializeFromJson()()
PatchDexterityContentGetattr()()
PatchDexterityDefaultAddForm()()
PatchDXContainerPastePermission()()
PatchDXCreateContentInContainer()()
PatchExceptionFormatter()()
PatchExtendedPathIndex()()
PatchInvokeFactory()()
PatchLDAPUserFolderEncoding()()
PatchMembershipToolCreateMemberarea()()
PatchMembershipToolSetLoginTimes()()
PatchNamedfileNamedDataConverter()()
PatchOFSRoleManager()()
PatchPlone43RC1Upgrade()()
PatchPloneProtectOnUserLogsIn()()
PatchPloneUserAllowed()()
PatchPloneUserGetRolesInContext()()
PatchResourceRegistriesURLRegex()()
PatchTransmogrifyDXSchemaUpdater()()
PatchWebDAVLockTimeout()()
PatchWorkflowTool()()
PatchZ2LogTimezone()()
PatchZ3CFormChangedField()()
PatchZ3CFormWidgetUpdate()()
ScrubBoboExceptions()()
