from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter


class LockingOperations(BrowserView):
    """Lock acquisition and stealing operations
    """

    def force_unlock_unstealable(self, redirect=True):
        """Steal the lock.

        If redirect is True, redirect back to the context URL, i.e. reload
        the page.
        """
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.clear_locks()
        if redirect:
            url = self.context.absolute_url()
            props_tool = getToolByName(self.context, 'portal_properties')
            if props_tool:
                types_use_view = props_tool.site_properties.typesUseViewActionInListings
                if self.context.portal_type in types_use_view:
                    url += '/view'

            self.request.RESPONSE.redirect(url)
