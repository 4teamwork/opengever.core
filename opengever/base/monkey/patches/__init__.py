from .create_mail_defaults import PatchCreateMailInContainer
from .default_values import PatchBuilderCreate
from .default_values import PatchDexterityContentGetattr
from .default_values import PatchDexterityDefaultAddForm
from .default_values import PatchDXCreateContentInContainer
from .default_values import PatchInvokeFactory
from .default_values import PatchZ3CFormChangedField
from .filter_trashed_from_catalog import PatchCatalogToFilterTrashedDocs
from .history_handler_tool import PatchCMFEditonsHistoryHandlerTool
from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
from .namedfile_data_converter import PatchNamedfileNamedDataConverter
from .paste_permission import PatchDXContainerPastePermission
from .plone_43rc1_upgrade import PatchPlone43RC1Upgrade
from .resource_registries_url_regex import PatchResourceRegistriesURLRegex
from .tz_for_log import PatchZ2LogTimezone
from .verify_object_paste import PatchCopyContainerVerifyObjectPaste
from .webdav_lock_timeout import PatchWebDAVLockTimeout


PatchBuilderCreate()()
PatchCatalogToFilterTrashedDocs()()
PatchCMFEditonsHistoryHandlerTool()()
PatchCopyContainerVerifyObjectPaste()()
PatchCreateMailInContainer()()
PatchDexterityContentGetattr()()
PatchDexterityDefaultAddForm()()
PatchDXContainerPastePermission()()
PatchDXCreateContentInContainer()()
PatchInvokeFactory()()
PatchLDAPUserFolderEncoding()()
PatchNamedfileNamedDataConverter()()
PatchPlone43RC1Upgrade()()
PatchResourceRegistriesURLRegex()()
PatchWebDAVLockTimeout()()
PatchZ2LogTimezone()()
PatchZ3CFormChangedField()()
