from opengever.base.pdfconverter import is_pdfconverter_enabled
from opengever.document.browser.download import DownloadConfirmationHelper
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.protect.utils import addTokenToUrl
from zope.publisher.browser import BrowserView


class TooltipView(BrowserView):

    def __init__(self, context, request):
        super(TooltipView, self).__init__(context, request)
        self.document = IContentListingObject(self.context)

    def get_url(self):
        return self.context.absolute_url()

    def preview_link_available(self):
        return self.document.is_document and is_pdfconverter_enabled()

    def edit_metadata_link_available(self):
        return not self.document.is_trashed

    def checkout_and_edit_link_available(self):
        if not self.document.is_document:
            return False
        return self.document.getObject().is_checkout_and_edit_available()

    def checkout_and_edit_link(self):
        return addTokenToUrl('{}/editing_document'.format(self.get_url()))

    def download_link_available(self):
        return self.document.digitally_available

    def download_link(self):
        dc_helper = DownloadConfirmationHelper()
        return (dc_helper
                .get_html_tag(self.get_url(),
                              additional_classes=['function-download-copy']))
