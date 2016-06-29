from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.tabbedview import _
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.protect.utils import addTokenToUrl
from Products.CMFPlone import PloneMessageFactory as pmf
from zope.globalrequest import getRequest
from zope.i18n import translate
import pkg_resources


try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    PDFCONVERTER_AVAILABLE = False
else:
    PDFCONVERTER_AVAILABLE = True


class DocumentLinkRenderer(object):

    def __init__(self, document):
        self.document = IContentListingObject(document)

    def is_bumblebeeable(self):
        return self.document.is_bumblebeeable()

    def get_url(self):
        return self.document.getURL()

    def get_css_class(self):
        return self.document.ContentTypeClass()

    def get_title(self):
        return self.document.Title()

    def preview_link_available(self):
        return self.document.is_document and PDFCONVERTER_AVAILABLE

    def preview_link(self):
        link = u'{}/@@download_pdfpreview'.format(self.get_url())
        label = translate(_(u'button_pdf_preview', u'PDF Preview'),
                          context=getRequest())
        return '<a class="action-pdf" href="{}">{}</a>'.format(
            link, label.decode('utf-8'))

    def edit_metadata_link_available(self):
        return not self.document.is_trashed

    def edit_metadata_link(self):
        link = u'{}/edit_checker'.format(self.get_url())
        label = translate(pmf(u'Edit metadata'), context=getRequest())
        return '<a class="action-edit" href="{}">{}</a>'.format(
            link, label.decode('utf-8'))

    def checkout_and_edit_link_available(self):
        return self.document.is_document

    def checkout_and_edit_link(self):
        link = addTokenToUrl('{}/editing_document'.format(self.get_url()))
        label = translate(pmf('Checkout and edit'), context=getRequest())
        return '<a class="action-checkout" href="{}">{}</a>'.format(
            link, label.decode('utf-8'))

    def download_link_available(self):
        return self.document.is_document

    def download_link(self):
        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(self.get_url(),
                                      additional_classes=['action-download'])

    def tooltip_actions(self):
        links = []
        if self.preview_link_available():
            links.append('<li>{}</li>'.format(self.preview_link()))

        if self.edit_metadata_link_available():
            links.append('<li>{}</li>'.format(self.edit_metadata_link()))

        if self.checkout_and_edit_link_available():
            links.append('<li>{}</li>'.format(self.checkout_and_edit_link()))

        if self.download_link_available():
            links.append('<li>{}</li>'.format(self.download_link()))

        return """
        """.join(links)

    def removed_marker(self):
        if self.document.is_removed:
            return "<span class='removed_document'></span>"
        return ''

    def get_showroom_class(self):
        if self.is_bumblebeeable():
            return 'showroom-item'
        return ''

    def get_showroom_data(self):
        return 'data-showroom-target="{overlay_url}" ' \
            'data-showroom-title="{title}"'.format(
                overlay_url=self.document.get_overlay_url(),
                title=self.document.get_overlay_title())

    def get_bumblebee_thumbnail(self):
        if self.is_bumblebeeable():
            return """
            <img src='{image_url}' alt='{title}' width="200" class="file-preview" />
            """.format(image_url=self.document.get_preview_image_url(),
                       title=self.get_title())

        return ''

    def render(self):
        return """
        <div class='linkWrapper'>
            {removed_marker}
            <a class='tabbedview-tooltip document_link {css_class} {showroom_class}'
                href='{url}' {showroom}>{title}</a>
            <div class='tabbedview-tooltip-data'>
                <div class='tooltip-header'>{title}</div>
                <div class='tooltip-breadcrumb'>{breadcrumbs}</div>
                <div class='tooltip-content'>
                    <ul class='tooltip-links'>
                        {tooltip_actions}
                    </ul>
                    <div class="preview">
                        {bumblebee_thumbnail}
                    </div>
                </div>
                <div class='bottomImage'></div>
            </div>
        </div>""".format(removed_marker=self.removed_marker(),
                         css_class=self.get_css_class(),
                         url=self.get_url(),
                         title=self.get_title(),
                         showroom=self.get_showroom_data(),
                         showroom_class=self.get_showroom_class(),
                         tooltip_actions=self.tooltip_actions(),
                         breadcrumbs=self.document.get_breadcrumbs(),
                         bumblebee_thumbnail=self.get_bumblebee_thumbnail())
