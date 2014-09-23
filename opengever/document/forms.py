from AccessControl import getSecurityManager
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from opengever.document.interfaces import NO_DOWNLOAD_INPUT_MODE
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from zope.component import queryMultiAdapter


class DocumentEditForm(DefaultEditForm):
    """Custom edit form for documents, which displays some
    different and customized edit modes.
    """

    def updateWidgets(self):
        """Using document specific formwidget.namedfile modes.
        """

        super(DocumentEditForm, self).updateWidgets()

        # get the checkin checkout manager
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            return

        filefields = [g.fields.get('file') for g in self.groups
                      if 'file' in g.fields]
        if len(filefields) > 0:
            file_field = filefields[0]

            current_user_id = getSecurityManager().getUser().getId()
            if self.context.digitally_available:
                if manager.get_checked_out_by() == current_user_id:
                    file_field.mode = NO_DOWNLOAD_INPUT_MODE
                else:
                    file_field.mode = NO_DOWNLOAD_DISPLAY_MODE
            else:
                file_field.mode = NO_DOWNLOAD_INPUT_MODE

DocumentEditView = layout.wrap_form(DocumentEditForm)
