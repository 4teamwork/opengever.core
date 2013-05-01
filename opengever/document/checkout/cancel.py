from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import getMultiAdapter
from zope.interface import Interface


class CancelDocuments(grok.View):
    """Cancel the checkout of one or more documents. This view is either
    called from a tabbed_view or folder_contents action (using the request
    parameter "paths") or directly on the document itself (without any
    request parameters).
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('cancel_document_checkouts')

    def render(self):

        # check whether we have paths or not
        paths = self.request.get('paths')

        # using "paths" is mandantory on any objects except for a document
        if not paths and not IDocumentSchema.providedBy(self.context):
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            # we assume the request came from the tabbed_view "documents"
            # tab on the dossier
            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

        elif paths:
            # lookup the objects to be handled using the catalog
            catalog = getToolByName(self.context, 'portal_catalog')
            objects = []
            for path in paths:
                query = dict(path={'query': path, 'depth': 0})
                obj = catalog(query)[0].getObject()
                objects.append(obj)

        else:
            # the context is the document
            objects = [self.context]

        # now, lets cancel every document
        for obj in objects:
            self.cancel(obj)

        # now lets redirect to an appropriate target..
        if len(objects) == 1:
            return self.request.RESPONSE.redirect(
                objects[0].absolute_url())

        else:
            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

    def cancel(self, obj):
        """Cancels a single document checkout.
        """

        # check out the document
        manager = getMultiAdapter((obj, self.request),
                                  ICheckinCheckoutManager)

        # is cancel allowed for this document?
        if not manager.is_cancel_allowed():
            msg = _(u'Could not cancel checkout on document ${title}',
                    mapping=dict(title=obj.Title().decode('utf-8')))
            IStatusMessage(self.request).addStatusMessage(msg, type='error')

        else:
            manager.cancel()

            # notify the user
            msg = _(u'Cancel checkout: ${title}',
                    mapping={'title': obj.Title().decode('utf-8')})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
