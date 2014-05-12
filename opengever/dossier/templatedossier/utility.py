from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.dossier.templatedossier.interfaces import ITemplateUtility


class TemplateFolderUtility(grok.GlobalUtility):
    grok.provides(ITemplateUtility)
    grok.name('opengever.templatedossier')

    def templateFolder(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        result = catalog(
            portal_type="opengever.dossier.templatedossier",
            sort_on='path')

        if result:
            return result[0].getPath()
        return None
