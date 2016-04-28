from .ldap_userfolder_encoding import PatchLDAPUserFolderEncoding
from .tz_for_log import PatchZ2LogTimezone


PatchLDAPUserFolderEncoding()()
PatchZ2LogTimezone()()
