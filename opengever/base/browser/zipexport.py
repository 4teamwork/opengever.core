from ftw.zipexport.browser.zipexportview import ZipExportView
from ftw.zipexport.browser.zipexportview import ZipSelectedExportView
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.workspace.utils import is_restricted_workspace_and_guest
from zExceptions import Forbidden


class GEVERZipExportView(ZipExportView):

    def __call__(self):
        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()

        return super(GEVERZipExportView, self).__call__()


class GEVERZipSelectedExportView(ZipSelectedExportView):

    def __call__(self):
        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()

        # XXX: Also make pseudo-relative paths work
        # (as sent by the new gever-ui)
        rewrite_path_list_to_absolute_paths(self.request)
        return super(GEVERZipSelectedExportView, self).__call__()
