from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.ogds.base.actor import Actor
from plone.app.layout.viewlets import content

try:
    from opengever.pdfconverter.behaviors.preview import IPreviewMarker
    PDFCONVERTER_AVAILABLE = True
except ImportError:
    PDFCONVERTER_AVAILABLE = False


class DocumentContentHistoryViewlet(content.ContentHistoryViewlet):
    """Customized content history viewlet for versioned OpenGever types
    (documents and mails).

    If the content type provides the IPreview behavior, an additional link
    is displayed to retrieve the PDF preview for that version.
    """

    def revisionHistory(self):
        history = super(DocumentContentHistoryViewlet, self).revisionHistory()
        for item in history:
            actor_id = item.get('actorid')
            actor = Actor.user(actor_id)
            item['user_link'] = actor.get_link()
        return history

    def previewSupported(self):
        if not PDFCONVERTER_AVAILABLE:
            # PDF Converter isn't available at all
            return False
        else:
            return IPreviewMarker.providedBy(self.context)

    def downloadLink(self):
        """Determines if the history viewlet should display a link to
        download the content as a file or a link to show the content with
        the default view."""
        if self.context.portal_type in ['opengever.document.document']:
            return True
        return False

    def get_download_copy_tag(self, version_id):
        dc_helper = DownloadConfirmationHelper()
        return dc_helper.get_html_tag(
            self.context.absolute_url(),
            url_extension="?version_id=%s" % version_id,
            additional_classes=['standalone', 'function-download-copy'])

    update = content.ContentHistoryViewlet.update
