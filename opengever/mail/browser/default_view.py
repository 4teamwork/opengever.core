from opengever.base.browser.default_view import OGDefaultView
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from opengever.propertysheets.form import omit_custom_properties_group


class MailDefaultView(OGDefaultView):
    """A customized default view for Dexterity content.

    On mails we don't want to display the message widget in DISPLAY mode
    because then it's possible to download a possibly private working copy
    of the message.
    """

    def update(self):
        super(MailDefaultView, self).update()
        self.groups = omit_custom_properties_group(self.groups)

    def updateWidgets(self):
        super(MailDefaultView, self).updateWidgets()
        field = self.groups[0].fields.get('message')
        if field:
            field.mode = NO_DOWNLOAD_DISPLAY_MODE
