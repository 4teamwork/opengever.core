from opengever.base.formutils import field_by_name
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from plone.dexterity.browser.edit import DefaultEditForm


class MailEditForm(DefaultEditForm):
    """Custom edit form for mails, which displays a custom edit mode for
    message.
    """

    def updateWidgets(self):
        super(MailEditForm, self).updateWidgets()

        # XXX: Maybe use IPrimaryFieldInfo here instead?
        field = field_by_name(self, 'message')
        field.mode = NO_DOWNLOAD_DISPLAY_MODE
