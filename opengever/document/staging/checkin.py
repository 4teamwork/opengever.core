
import os

from Acquisition import aq_inner, aq_parent
from five import grok
from zope.interface import Interface
from zope import schema
from z3c.form import form, field, button
from z3c.form.interfaces import HIDDEN_MODE

from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.interfaces import IDexterityContent
from plone.z3cform import layout

from opengever.document import _
from opengever.document.staging.manager import ICheckinCheckoutManager
from opengever.document.document import IDocumentSchema


class NoItemsSelected(Exception):
    pass


# ---- CHECKIN ----
class ICheckinCommentFormSchema(Interface):
    """ Form schema for entering a journal comment in checkin procedure
    """
    paths = schema.TextLine(title=u'Selected Items') # hidden
    redirect_url = schema.TextLine(title=u'Redirect URL') # hidden
    comment = schema.Text(
        title=_(u'label_checkin_journal_comment',
                default=u'Journal Comment'),
        description=_(u'help_checkin_journal_comment',
                      default=u'Describe, why you checkin the selected documents'),
        required=True,
        )



class CheckinCommentForm(form.Form):
    fields = field.Fields(ICheckinCommentFormSchema)
    ignoreContext = True
    label = _(u'heading_checkin_comment_form', u'Checkin Documents')

    @button.buttonAndHandler(_(u'button_checkin', default=u'Checkin'))
    def checkin_button_handler(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            last_baseline = None
            for obj in self.objects:
                last_baseline = self.checkin_object(obj, data['comment'])
            redirect_url = self.redirect_url
            if redirect_url=='baseline' and last_baseline:
                redirect_url = last_baseline.absolute_url()
            return self.request.RESPONSE.redirect(redirect_url)

    def checkin_object(self, obj, comment):
        manager = ICheckinCheckoutManager(obj)
        return manager.checkin(comment, show_status_message=True)

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
        super(CheckinCommentForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)
        self.widgets['redirect_url'].mode = HIDDEN_MODE
        self.widgets['redirect_url'].value = self.redirect_url



class CheckinDocuments(layout.FormWrapper, grok.CodeView):
    """ Checks in one or more documents.
    Is called by a folder_contents action or a tabbed-view action
    """
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('checkin_documents')
    form = CheckinCommentForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)

    def render(self):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        try:
            return layout.FormWrapper.__call__(self, *args, **kwargs)
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



class CheckinSingleDocument(grok.CodeView):
    grok.context(IDocumentSchema)
    grok.name('document-checkin')

    def render(self):
        response = self.request.RESPONSE
        parent = aq_parent( aq_inner( self.context ) )
        path = os.path.join(
            parent.absolute_url(),
            'checkin_documents',
            '?paths:list=%s&orig_template=baseline' % (
                '/'.join(self.context.getPhysicalPath()),
                )
            )
        return response.redirect(path)
