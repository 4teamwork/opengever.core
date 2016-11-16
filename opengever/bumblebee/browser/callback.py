from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from opengever.document.archival_file import ArchivalFileConverter


class StoreArchivalFile(BaseConvertCallbackView):
    """Callback endpoint for the Bumblebee archival file conversion.
    The ArchivalFileConverter triggers the conversion and defines this view
    as callback. Therefore this view will be called by the Bumblebee app.
    """

    def handle_success(self, mimetype, file_data):
        ArchivalFileConverter(self.context).store_file(file_data, mimetype)

    def handle_error(self):
        ArchivalFileConverter(
            self.context).handle_temporary_conversion_failure()

    def handle_skipped(self):
        ArchivalFileConverter(
            self.context).handle_permanent_conversion_failure()
