
import os

from Acquisition import aq_inner, aq_parent
from five import grok
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage

from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.document import _
from opengever.document.document import IDocumentSchema

class CancelCheckout(grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('cancel_document_checkouts')

    def render(self):
        objects = self.objects
        last_baseline = None
        if len(objects)>0:
            for obj in objects:
                manager = ICheckinCheckoutManager(obj)
                last_baseline = manager.cancel(show_status_message=True)
        else:
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
        response = self.request.RESPONSE
        redirect_url = self.request.get('orig_template', None)
        if not redirect_url:
            redirect_url = self.request.get('HTTP_REFERER', None)
        if not redirect_url:
            redirect_url = '.'
        if redirect_url=='baseline':
            redirect_url = last_baseline.absolute_url()
        return response.redirect(redirect_url)

    @property
    def objects(self):
        lookup = lambda p:self.context.restrictedTraverse(str(p))
        paths = self.request.get('paths', [])
        return [lookup(p) for p in paths]


class CancelSingleCheckoutDocument(grok.CodeView):
    grok.context(IDocumentSchema)
    grok.name('document-cancel-checkout')

    def render(self):
        response = self.request.RESPONSE
        parent = aq_parent( aq_inner( self.context ) )
        path = os.path.join(
            parent.absolute_url(),
            'cancel_document_checkouts',
            '?paths:list=%s&orig_template=baseline' % (
                '/'.join(self.context.getPhysicalPath()),
                )
            )
        return response.redirect(path)
