from opengever.document.browser.download import DownloadConfirmationHelper
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.protect.utils import addTokenToUrl
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.globalrequest import getRequest
import pkg_resources


try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    PDFCONVERTER_AVAILABLE = False
else:
    PDFCONVERTER_AVAILABLE = True


class DocumentLinkWidget(object):

    template = ViewPageTemplateFile('document_link.pt')

    def __init__(self, document):
        self.document = IContentListingObject(document)
        self.context = self.document
        self.request = getRequest()

    def get_url(self):
        return self.document.getURL()

    def get_css_class(self):
        classes = ['tabbedview-tooltip', 'document_link',
                   self.document.ContentTypeClass()]

        if self.document.is_bumblebeeable():
            classes.append('showroom-item')

        return ' '.join(classes)

    def get_title(self):
        return self.document.Title().decode('utf-8')

    def preview_link_available(self):
        return self.document.is_document and PDFCONVERTER_AVAILABLE

    def edit_metadata_link_available(self):
        return not self.document.is_trashed

    def checkout_and_edit_link_available(self):
        return self.document.is_document

    def checkout_and_edit_link(self):
        return addTokenToUrl('{}/editing_document'.format(self.get_url()))

    def download_link_available(self):
        return self.document.is_document

    def download_link(self):
        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(self.get_url(),
                                      additional_classes=['action-download'])

    def render(self):
        return self.template(self, self.request)
