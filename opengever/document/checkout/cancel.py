from ftw.mail.mail import IMail
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.exceptions import NoItemsSelected
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.tabbedview.utils import get_containing_document_tab_url
from plone import api
from plone.z3cform import layout
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface


class CancelDocuments(BrowserView):
    """Cancel the checkout of one or more documents. This view is either
    called from a tabbed_view or folder_contents action (using the request
    parameter "paths") or directly on the document itself (without any
    request parameters).
    """

    def __call__(self):
        # check whether we have paths or not
        paths = self.request.get('paths')

        # using "paths" is mandantory on any objects except for a document
        if not paths and not IDocumentSchema.providedBy(self.context):
            msg = _(u'You have not selected any documents.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')

            # we assume the request came from the tabbed_view "documents"
            # tab on the dossier
            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

        elif paths:
            # lookup the objects to be handled using the catalog
            catalog = api.portal.get_tool('portal_catalog')
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
        if IMail.providedBy(obj):
            msg = _(u'msg_cancel_checkout_on_mail_not_possible',
                    default=u'Could not cancel checkout on document ${title}, '
                    'mails does not support the checkin checkout process.',
                    mapping={'title': obj.Title().decode('utf-8')})
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return

        # check out the document
        manager = getMultiAdapter((obj, self.request),
                                  ICheckinCheckoutManager)

        # is cancel allowed for this document?
        if not manager.is_cancel_allowed():
            msg = _(u'Could not cancel checkout on document ${title}.',
                    mapping=dict(title=obj.Title().decode('utf-8')))
            api.portal.show_message(
                message=msg, request=self.request, type='error')

        else:
            manager.cancel()
            # notify the user
            msg = _(u'Cancel checkout: ${title}',
                    mapping={'title': obj.Title().decode('utf-8')})
            api.portal.show_message(
                message=msg, request=self.request, type='info')


class CancelDocumentCheckoutConfirmation(BrowserView):
    """Confirmation overlay view to cancel the checkout of a document.
    This view is called directly on the document itself
    (without any request parameters).
    """

    def get_checkout_cancel_url(self):
        url = u'{}/@@cancel_document_checkouts'.format(
            self.context.absolute_url())
        return url


class IMultiCheckoutCancelSchema(Interface):
    """Form schema to confirm multi checkout cancel."""

    paths = schema.TextLine(title=u'Selected Items')


class MultiCheckoutCancelForm(form.Form):
    """Form to confirm cancelation of checkout for mutliple documents."""

    fields = field.Fields(IMultiCheckoutCancelSchema)
    ignoreContext = True

    def __init__(self, context, request):
        super(MultiCheckoutCancelForm, self).__init__(context, request)

    def cancel_checkout(self, force=False):
        self.request.set("paths", self.get_document_paths())
        return CancelDocuments(self.context, self.request).__call__()

    @button.buttonAndHandler(_(u'Cancel checkout'))
    def cancel_checkout_button(self, action):
        return self.cancel_checkout()

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(
            get_containing_document_tab_url(self.context))

    def get_document_paths(self):
        if self.widgets:
            field_name = self.prefix + self.widgets.prefix + 'paths'
            value = self.request.get(field_name, False)
            if value:
                return value.split(';;')
        return self.request.get('paths', [])

    def get_filenames(self):
        portal = api.portal.get()
        paths = self.get_document_paths()
        return [portal.unrestrictedTraverse(path.split("/")).title_or_id() for path in paths]

    def updateWidgets(self):
        super(MultiCheckoutCancelForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.get_document_paths())


class CancelDocumentsCheckoutConfirmation(layout.FormWrapper):
    """Checkin multiple documents with comment.

    This view is called from a tabbed_view.
    """

    form = MultiCheckoutCancelForm

    def __call__(self, *args, **kwargs):
        try:
            return layout.FormWrapper.__call__(self, *args, **kwargs)
        except NoItemsSelected:
            msg = _(u'You have not selected any documents.')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')

            return self.request.RESPONSE.redirect(
                get_containing_document_tab_url(self.context))
