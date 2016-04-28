from .create_mail_defaults import PatchCreateMailInContainer
from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
from .paste_permission import PatchDXContainerPastePermission
from .tz_for_log import PatchZ2LogTimezone
from .webdav_lock_timeout import PatchWebDAVLockTimeout


PatchCreateMailInContainer()()
PatchDXContainerPastePermission()()
PatchLDAPUserFolderEncoding()()
PatchWebDAVLockTimeout()()
PatchZ2LogTimezone()()
