from opengever.base.monkey.patching import MonkeyPatch
import os


class PatchBaseOrderedViewletManagerExceptions(MonkeyPatch):
    """Patch exceptions so that all are raised during viewlet rendering.

    Only apply the patch in development mode.
    """
    def __call__(self):
        if not os.environ.get('IS_DEVELOPMENT_MODE', False):
            return

        from plone.app.viewletmanager.manager import BaseOrderedViewletManager

        new_exceptions = (Exception,)
        self.patch_value(BaseOrderedViewletManager,
                         '_exceptions_handled_elsewhere',
                         new_exceptions)
