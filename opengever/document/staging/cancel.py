
from five import grok
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage

from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.document import _

class CancelCheckout(grok.CodeView):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('cancel_document_checkouts')

    def render(self):
        objects = self.objects
        if len(objects)>0:
            for obj in objects:
                manager = ICheckinCheckoutManager(obj)
                manager.cancel(show_status_message=True)
        else:
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
        response = self.request.RESPONSE
        redirect_url = self.request.get('orig_template', None)
        if not redirect_url:
            redirect_url = self.request.get('HTTP_REFERER', None)
        if not redirect_url:
            redirect_url = '.'
        return response.redirect(redirect_url)

    @property
    def objects(self):
        lookup = lambda p:self.context.restrictedTraverse(str(p))
        paths = self.request.get('paths', [])
        return [lookup(p) for p in paths]
