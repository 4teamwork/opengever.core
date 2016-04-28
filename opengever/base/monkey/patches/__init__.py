from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
from .tz_for_log import PatchZ2LogTimezone
from .webdav_lock_timeout import PatchWebDAVLockTimeout


PatchLDAPUserFolderEncoding()()
PatchWebDAVLockTimeout()()
PatchZ2LogTimezone()()
