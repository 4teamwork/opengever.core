from opengever.base.monkey.patching import MonkeyPatch


class PatchDXContainerPastePermission(MonkeyPatch):
    """Change permission for manage_pasteObjects to "Add portal content"

    See https://dev.plone.org/ticket/9177
    See also https://web.archive.org/web/20151023012935/https://dev.plone.org/ticket/13820
    See also https://community.plone.org/t/plone-paste-permissions/7155
    XXX: Find a way to do this without patching __ac_permissions__ directly
    """

    def __call__(self):
        from Products.CMFCore.permissions import AddPortalContent

        from plone.dexterity.content import Container
        self.patch_class_security(
            Container, 'manage_pasteObjects', AddPortalContent)
