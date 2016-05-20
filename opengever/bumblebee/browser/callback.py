from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from opengever.document.archival_file import ArchivalFileConverter
import base64


class StoreArchivalFile(BaseConvertCallbackView):

    def handle_success(self, mimetype, file_data):
        ArchivalFileConverter(self.context).store_file(file_data)

    def handle_error(self):
        ArchivalFileConverter(self.context).handle_conversion_failure()

    def verify_token(self):
        # TODO: Remove and let the BaseConvertCallbackView check the token.
        return True
