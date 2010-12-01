from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import webdav_enabled
from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import queryMultiAdapter
from zope.interface import Interface


class ExternalEditingAllowed(grok.View):
    """View for deciding whether the user is allowed to edit the current object
    with external editor or not.
    """

    grok.context(Interface)
    grok.name('external_editing_allowed')
    grok.require('zope2.View')

    def render(self):
        parent = aq_parent(aq_inner(self.context))

        # not allowed for anonymous users
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.isAnonymousUser():
            return False

        # if webdav is not allowed, we cannot externally edit
        if not webdav_enabled(self.context, parent):
            return False

        # only allowed on documents
        if not IDocumentSchema.providedBy(self.context):
            return False

        # only allowed, when there already is a file
        if not self.context.file:
            return False

        # only allowed when the current user has checked out the document
        current_user_id = getSecurityManager().getUser().getId()
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)

        if not manager or manager.checked_out() != current_user_id:
            return False

        # Content may provide data to the external editor ?
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return not not portal.externalEditLink_(self.context)
