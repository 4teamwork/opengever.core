from plone.dexterity.browser.edit import DefaultEditForm
from z3c.form.interfaces import DISPLAY_MODE


class EditForm(DefaultEditForm):
    """Standard edit form, but shows the message field only in Display Mode"""

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()

        self.groups[0].fields.get('message').mode = DISPLAY_MODE
