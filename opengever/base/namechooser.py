from plone.app.content.namechooser import NormalizingNameChooser
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import implementer


@implementer(INameChooser)
@adapter(IPloneSiteRoot)
class GEVERRootNameChooser(NormalizingNameChooser):
    """Custom NameChooser for the Plone site root in GEVER.

    This allows us to control names for content types that are directly added
    to the Plone site root, like contact folders or workspace roots.

    These are often singleton-like objects, and their name is not usually
    derived from their title, but rather a standardized short name.

    We therefore hook ourselves in here to *suggest* that base prefix as the
    name, and let the default NormalizingNameChooser take over from there. In
    the common case that the object is the first of its type, this will result
    in the prefix getting chosen as the full name.
    """

    def __init__(self, context):
        self.context = context

    def chooseName(self, name, obj):
        if obj.portal_type == 'opengever.workspace.root':
            if not name:
                name = 'workspaces'

            # Let NormalizingNameChooser take over from here.
            # We just hooked in here to suggest 'workspaces' as the base,
            # and fall back to the default behavior for the rest.

        return super(GEVERRootNameChooser, self).chooseName(name, obj)
