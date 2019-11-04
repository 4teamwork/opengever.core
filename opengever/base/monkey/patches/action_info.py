from opengever.base.monkey.patching import MonkeyPatch
from Products.CMFCore.utils import _checkPermission


class PatchActionInfo(MonkeyPatch):
    """We patch the _checkPermissions() method of the ActionInfo object
    in order to also consider our 'file_actions' category one that should
    have its actions' permissions checked on the context.

    Without this, the permissions would be checked on the Plone Site instead.
    """

    def __call__(self):

        def _checkPermissions(self, ec):
            """ Check permissions in the current context.
            """
            category = self['category']
            object = ec.contexts['object']
            if object is not None and ( category.startswith('object') or
                                        category.startswith('workflow') or
                                        category.startswith('file') or  # <-- patched
                                        category.startswith('document') ):
                context = object
            else:
                folder = ec.contexts['folder']
                if folder is not None and category.startswith('folder'):
                    context = folder
                else:
                    context = ec.contexts['portal']

            for permission in self._permissions:
                if _checkPermission(permission, context):
                    return True
            return False

        from Products.CMFCore.ActionInformation import ActionInfo
        locals()['__patch_refs__'] = False

        self.patch_refs(ActionInfo, '_checkPermissions', _checkPermissions)
