from opengever.base.monkey.patching import MonkeyPatch


class PatchDXContainerPastePermission(MonkeyPatch):
    """Change permission for manage_pasteObjects to "Add portal content"

    See https://dev.plone.org/ticket/9177
    XXX: Find a way to do this without patching __ac_permissions__ directly
    """

    def __call__(self):
        from Products.CMFCore.permissions import AddPortalContent

        from plone.dexterity.content import Container
        self.patch_class_security(
            Container, 'manage_pasteObjects', AddPortalContent)
