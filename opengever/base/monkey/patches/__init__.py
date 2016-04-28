from .create_mail_defaults import PatchCreateMailInContainer
from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
from .namedfile_data_converter import PatchNamedfileNamedDataConverter
from .paste_permission import PatchDXContainerPastePermission
from .tz_for_log import PatchZ2LogTimezone
from .webdav_lock_timeout import PatchWebDAVLockTimeout


PatchCreateMailInContainer()()
PatchDXContainerPastePermission()()
PatchLDAPUserFolderEncoding()()
PatchNamedfileNamedDataConverter()()
PatchWebDAVLockTimeout()()
PatchZ2LogTimezone()()
