from ftw.zipexport.browser.zipexportview import ZipSelectedExportView
from opengever.base.utils import rewrite_path_list_to_absolute_paths


class GEVERZipSelectedExportView(ZipSelectedExportView):

    def __call__(self):
        # XXX: Also make pseudo-relative paths work
        # (as sent by the new gever-ui)
        rewrite_path_list_to_absolute_paths(self.request)
        return super(GEVERZipSelectedExportView, self).__call__()
