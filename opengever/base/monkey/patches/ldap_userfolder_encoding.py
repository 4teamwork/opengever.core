from opengever.base.monkey.patching import MonkeyPatch


class PatchLDAPUserFolderEncoding(MonkeyPatch):
    """Patch LDAPUserFolder's default encoding to 'utf-8' instead of 'latin1'.
    """

    def __call__(self):
        new_encoding = 'utf-8'

        from Products.LDAPUserFolder import utils
        self.patch_value(utils, 'encoding', new_encoding)

        from Products.LDAPUserFolder import LDAPUser
        self.patch_value(LDAPUser, 'encoding', new_encoding)
