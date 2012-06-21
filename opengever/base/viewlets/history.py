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

    update = content.ContentHistoryViewlet.update
