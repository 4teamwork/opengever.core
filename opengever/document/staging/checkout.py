import os

from Acquisition import aq_inner, aq_parent
from five import grok
from zope.interface import Interface
from zope import schema
from z3c.form import form, field, button
from z3c.form.interfaces import HIDDEN_MODE

from plone.dexterity.interfaces import IDexterityContent
from plone.z3cform import layout
from Products.statusmessages.interfaces import IStatusMessage

from plone.directives.form import widget
from z3c.form.browser import checkbox

from opengever.document import _
from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.document.document import IDocumentSchema

class NoItemsSelected(Exception):
    pass

# ---- CHECKOUT ----
class ICheckoutCommentFormSchema(Interface):
    """ Form schema for entering a journal comment in checkout procedure
    """
    paths = schema.TextLine(title=u'Selected Items') # hidden
    redirect_url = schema.TextLine(title=u'Redirect URL') # hidden
    comment = schema.Text(
        title=_(u'label_checkout_journal_comment',
                default=u'Journal Comment'),
        description=_(u'help_checkout_journal_comment',
                      default=u'Describe, why you checkout the selected documents'),
        required=False,
        )
    
    
    open_extern = schema.Bool(
        title = _(u'label_open_extern', default='external editor'),
        description = _(u'help_open_extern', default='open with a external editor'),
        required = False,
        )
    widget(open_extern=checkbox.SingleCheckBoxFieldWidget)

class CheckoutCommentForm(form.Form):
    fields = field.Fields(ICheckoutCommentFormSchema)
    ignoreContext = True
    label = _(u'heading_checkout_comment_form', u'Checkout Documents')

    @button.buttonAndHandler(_(u'button_checkout', default=u'Checkout'))
    def checkout_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            last_wc = None
            for obj in self.objects:
                last_wc = self.checkout_object(obj, data['comment'])
            redirect_url = self.redirect_url
            if redirect_url=='wc' and last_wc:
                redirect_url = last_wc.absolute_url()
            if data['open_extern']:
                redirect_url += '?externaledit=1'
            return self.request.RESPONSE.redirect(redirect_url)

    def checkout_object(self, obj, comment):
        manager = ICheckinCheckoutManager(obj)
        return manager.checkout(comment, show_status_message=True)

    @property
    def objects(self):
        """ Returns a list of the objects selected in folder contents or
        tabbed view
        """
        lookup = lambda p:self.context.restrictedTraverse(str(p))
        return [lookup(p) for p in self.item_paths]

    @property
    def item_paths(self):
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value
        value = self.request.get('paths')
        if not value:
            raise NoItemsSelected
        return value

    @property
    def redirect_url(self):
        field_name = self.prefix + self.widgets.prefix + 'redirect_url'
        value = self.request.get(field_name, False)
        if value:
            return value
        value = self.request.get('orig_template')
        if not value:
            value = self.request.get('HTTP_REFERER')
        if not value:
            value = '.'
        return value

    def updateWidgets(self):
        super(CheckoutCommentForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)
        self.widgets['redirect_url'].mode = HIDDEN_MODE
        self.widgets['redirect_url'].value = self.redirect_url



class CheckoutDocuments(layout.FormWrapper, grok.CodeView):
    """ Checks out one or more documents.
    Is called by a folder_contents action or a tabbed-view action
    """
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('checkout_documents')
    form = CheckoutCommentForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)

    def render(self):
        raise NotImplemented

    def __call__(self):
        try:
            return layout.FormWrapper.__call__(self)
        except NoItemsSelected:
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            response = self.request.RESPONSE
            redirect_url = self.request.get('orig_template', None)
            if not redirect_url:
                redirect_url = self.request.get('HTTP_REFERER', None)
            if not redirect_url:
                redirect_url = '.'
            return response.redirect(redirect_url)


class CheckoutSingleDocument(grok.CodeView):
    grok.context(IDocumentSchema)
    grok.name('document-checkout')

    def render(self):
        response = self.request.RESPONSE
        parent = aq_parent( aq_inner( self.context ) )
        path = os.path.join(
            parent.absolute_url(),
            'checkout_documents',
            '?paths:list=%s&orig_template=wc' % (
                '/'.join(self.context.getPhysicalPath()),
                )
            )
        return response.redirect(path)