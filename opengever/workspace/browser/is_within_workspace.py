from opengever.workspace.utils import is_within_workspace
from Products.Five import BrowserView


class IsWithinWorkspaceView(BrowserView):
    def __call__(self):
        return is_within_workspace(self.context)
