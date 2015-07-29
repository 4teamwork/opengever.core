from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout


class MailEditForm(DefaultEditForm):
    """Custom edit form for mails, which displays a custom edit mode for
    message.
    """

    def updateWidgets(self):
        super(MailEditForm, self).updateWidgets()

        field = self.groups[0].fields.get('message')
        if field:
            field.mode = NO_DOWNLOAD_DISPLAY_MODE


MailEditView = layout.wrap_form(MailEditForm)
