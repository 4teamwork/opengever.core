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
        ArchivalFileConverter(self.context).handle_conversion_failure()

    def verify_token(self):
        # XXX currently the bumblebee app does not send a token
        # https://github.com/4teamwork/bumblebee/issues/15
        # TODO: Remove and let the BaseConvertCallbackView check the token.
        return True
