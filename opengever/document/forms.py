"""Document form customizations.
"""

from AccessControl import getSecurityManager
from opengever.document.interfaces import ICheckinCheckoutManager
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form.interfaces import DISPLAY_MODE
from zope.component import queryMultiAdapter


class DocumentEditForm(DefaultEditForm):
    """Custom edit form for documents, which hides the file field
    when document is not checked out.
    """

    def updateWidgets(self):
        super(DocumentEditForm, self).updateWidgets()

        # get the checkin checkout manager
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            return

        current_user_id = getSecurityManager().getUser().getId()
        if self.context.digitally_available and (not manager.checked_out() \
                or manager.checked_out() != current_user_id):
            filefields = [g.fields.get('file') for g in self.groups
                          if 'file' in g.fields]
            if len(filefields) > 0:
                filefields[0].mode = DISPLAY_MODE


DocumentEditView = layout.wrap_form(DocumentEditForm)
