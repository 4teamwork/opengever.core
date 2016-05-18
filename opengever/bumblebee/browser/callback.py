from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from opengever.document.archival_file import ArchivalFileConverter
import base64


class StoreArchivalFile(BaseConvertCallbackView):

    def handle_success(self):
        ArchivalFileConverter(self.context).store_file(self.get_file_data())
        super(StoreArchivalFile, self).handle_success()

    def verify_token(self):
        # TODO: Remove and let the BaseConvertCallbackView check the token.
        return True

    def get_file_data(self):
        file_info, data = self.get_body().get('data').split(',')
        return base64.b64decode(data)
