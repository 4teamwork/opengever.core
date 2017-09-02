from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.interface import Interface


class CheckoutDocuments(grok.View):
    """View for checking out one or more document. This view is either
    called from a tabbed_view / folder_contents action (using the request
    parameter "paths") or directly on the document itself (without any
    request parameters).
    When calling the view directly on the document and submitting
    mode=external in the request, the external editor will automatically
    be called.
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('checkout_documents')

    def render(self):
        # check whether we have paths or not
        paths = self.request.get('paths')

        # using "paths" is mandantory on any objects except for a document
        if not paths and not IDocumentSchema.providedBy(self.context):
            msg = _(u'You have not selected any documents.')
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

        # now, lets checkout every document
        for obj in objects:
            if not IDocumentSchema.providedBy(obj):
                # notify the user. we have a no-checkoutable object
                msg = _(
                    u'Could not check out object: ${title}, '
                    'it is not a document.',
                    mapping={'title': obj.Title().decode('utf-8')})
                IStatusMessage(
                    self.request).addStatusMessage(msg, type='error')
                continue

            self.checkout(obj)

        # lets register a redirector for starting external
        # editor - if requested
        external_edit = self.request.get('mode') == 'external'

        # now lets redirect to an appropriate target..
        if len(objects) == 1:
            if external_edit:
                objects[0].setup_external_edit_redirect(self.request)
            return self.request.RESPONSE.redirect(
                objects[0].absolute_url())

        else:
            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

    def checkout(self, obj):
        """Checks out a single document object."""
        # Check out the document
        manager = getMultiAdapter((obj, self.request), ICheckinCheckoutManager)

        # is checkout allowed for this document?
        if not manager.is_checkout_allowed():
            msg = _(u'Could not check out document ${title}.',
                    mapping={'title': obj.Title().decode('utf-8')})
            IStatusMessage(self.request).addStatusMessage(msg, type='error')

        else:
            # check it out
            manager.checkout()

            # notify the user
            msg = _(u'Checked out: ${title}',
                    mapping={'title': obj.Title().decode('utf-8')})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
