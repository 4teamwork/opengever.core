from Products.PythonScripts.standard import url_quote
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.Five.browser import BrowserView
from Acquisition import aq_inner
from Products.TinyMCE.browser.interfaces.style import ITinyMCEStyle

TINYMCE_BANNED_STYLES = [
    "++theme++plonetheme.teamraum/css/responsive.css",
    "++resource++ftw.mobilenavigation/navigation.css",
    ]


class TinyMCEStyle(BrowserView):
    """TinyMCE Style"""
    implements(ITinyMCEStyle)

    def getStyle(self):
        """Returns a stylesheet with all content styles"""

        self.request.response.setHeader('Content-Type', 'text/css')

        registry = getToolByName(aq_inner(self.context), 'portal_css')
        registry_url = registry.absolute_url()
        context = aq_inner(self.context)

        styles = registry.getEvaluatedResources(context)
        skinname = url_quote(aq_inner(self.context).getCurrentSkinName())
        result = []
        user_agent = self.request.get('HTTP_USER_AGENT', 'browser')

        for style in styles:
            if style.getMedia() not in ('print', 'projection') and \
                    style.getRel() == 'stylesheet' and \
                    style.getId() not in TINYMCE_BANNED_STYLES:
                # do not load Internet Explorer conditional styles on non IE
                # browsers
                if not "Trident" in user_agent and \
                        style.getConditionalcomment():
                    continue
                if style.isExternalResource():
                    src = style.getId()
                else:
                    src = "<!-- @import url(%s/%s/%s); -->" % (
                        registry_url, skinname, style.getId())
                result.append(src)

        # BBB 2010-07-24 Support Plone 3
        portal_migration = getToolByName(self.context, 'portal_migration')
        if hasattr(portal_migration, 'getInstanceVersionTuple'):
            major_version = portal_migration.getInstanceVersionTuple()[0]
            if major_version == 3:
                css = self.context.restrictedTraverse(
                    'tiny_mce_plone3.css')(self.context)
                result.append(css)

        return "\n".join(result)
