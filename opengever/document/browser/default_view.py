from opengever.base.browser.default_view import OGDefaultView
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE


class DocumentDefaultView(OGDefaultView):
    """A customized default view for Dexterity content.

    On documents, we don't want to display the file widget in DISPLAY mode
    because then it's possible to download a possibly private working copy
    of the file.
    """

    def updateWidgets(self):
        super(DocumentDefaultView, self).updateWidgets()
        field = self.groups[0].fields.get('file')
        if field:
            field.mode = NO_DOWNLOAD_DISPLAY_MODE
