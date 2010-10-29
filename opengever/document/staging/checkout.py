from Acquisition import aq_inner, aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from zope.interface import Interface
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.base.interfaces import IRedirector

import os


class CheckoutDocuments(grok.CodeView):
    """ Checks out one or more documents.
    Is called by a folder_contents action or a tabbed-view action
    or from the CheckoutSingleDocument View.
    """
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('checkout_documents')

    def render(self):
        paths = self.request.get('paths')
        if not paths:
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')

            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())
        objs = self.objects(paths)
        for obj in objs:
            manager = ICheckinCheckoutManager(obj)
            last_wc = manager.checkout('', show_status_message=True)

        # redirecting
        # when only one files redirect to the working copy
        # when mutlitple files redirect to the documents tab
        if len(objs) == 1:
            redirect_url = last_wc.absolute_url()
            if self.request.get('mode') == 'external':
                redirector = IRedirector(self.request)
                redirector.redirect(
                    '%s?externaledit=1' % redirect_url)
        else:
            redirect_url = '%s#documents' % self.context.absolute_url()

        return self.request.RESPONSE.redirect(redirect_url)

    def objects(self, paths):
        """ Returns a list of the objects selected in folder contents or
        tabbed view
        """
        catalog = self.context.portal_catalog

        def lookup(path):
            query = {
                'path': {
                    'query': path,
                    'depth': 0,
                    }
                }
            return catalog(query)[0].getObject()
        return [lookup(p) for p in paths]


class CheckoutSingleDocument(grok.View):
    """A view wich set the request parameters for the acutal contetxt,
    and redirect to the CheckoutDocuments view."""
    grok.context(IDocumentSchema)
    grok.name('document-checkout')

    def render(self):
        response = self.request.RESPONSE
        parent = aq_parent(aq_inner(self.context))
        path = os.path.join(
            parent.absolute_url(),
            'checkout_documents',
            '?paths:list=%s&mode=%s' % (
                '/'.join(self.context.getPhysicalPath()),
                self.request.get('mode'),
                )
            )
        return response.redirect(path)
