from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.ogds.base.utils import get_current_client
from plone.app.layout.viewlets import common
from plone.app.layout.viewlets.interfaces import IPortalHeader
from plone.memoize import ram
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface


class ClientID(grok.Viewlet):
    grok.context(Interface)
    grok.name("opengever.clientid")
    grok.viewletmanager(IPortalHeader)

    @ram.cache(lambda *a, **kw: True)
    def get_title(self):
        try:
            current_client = get_current_client()
        except (ComponentLookupError, ValueError):
            return ''
        else:
            return current_client.title


class OpengeverContentViewsViewlet(common.ContentViewsViewlet):
    index = ViewPageTemplateFile('contentviews.pt')
