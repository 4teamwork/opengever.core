from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from plone.directives import dexterity


class View(dexterity.DisplayForm):
    grok.context(IDocumentSchema)
    grok.require("zope2.View")

    def updateWidgets(self):
        super(View, self).updateWidgets()
        field = self.groups[0].fields.get('file')
        if field:
            field.mode = NO_DOWNLOAD_DISPLAY_MODE
