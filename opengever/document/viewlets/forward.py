from five import grok
from opengever.document.document import IDocumentSchema
from plone.app.layout.viewlets.interfaces import IBelowContentTitle


class ForwardViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.document.ForwardViewlet')
    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)

    def render(self):
        if self.request.get("externaledit", None):
            return '<script language="JavaScript">jq(function(){window.location.href="' + str(
                self.context.absolute_url()) + '/external_edit"})</script>'
        return ''
