from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.exceptions import NoItemsSelected
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.tabbedview.utils import get_containg_document_tab_url
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import form, field, button
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface


class MultiCheckinController(object):
    """ Proviedes checkin functionality
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def checkin(self, documents_paths, comment=None):
        objects_str = [p.encode('utf-8') for p in documents_paths]
        objects = [self.context.unrestrictedTraverse(p) for p in objects_str]

        for obj in objects:
            if IDocumentSchema.providedBy(obj):
                manager = getMultiAdapter((obj, obj.REQUEST),
                                          ICheckinCheckoutManager)

                if not manager.is_checkin_allowed():
                    msg = _(
                        u'Could not check in document ${title}',
                        mapping=dict(title=obj.Title().decode('utf-8')))
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')

                else:
                    manager.checkin(comment)
                    msg = _(
                        u'Checked in: ${title}',
                        mapping=dict(title=obj.Title().decode('utf-8')))
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='info')

            else:
                title = obj.Title()
                if not isinstance(title, unicode):
                    title = title.decode('utf-8')
                msg = _(
                    u'Could not check in ${title}, it is not a document.',
                    mapping=dict(title=title))
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')


def get_document_paths(context, request):
    # from folder_contents / tabbed_view?
    value = request.get('paths')
    if value:
        return value

    # from the context?
    if IDocumentSchema.providedBy(context):
        return ['/'.join(context.getPhysicalPath())]

    # nothing found..
    raise NoItemsSelected


class ICheckinCommentFormSchema(Interface):
    """ Form schema for entering a journal comment in checkin procedure
    """

    # hidden by form
    paths = schema.TextLine(title=u'Selected Items')

    comment = schema.Text(
        title=_(u'label_checkin_journal_comment',
                default=u'Journal Comment'),
        description=_(u'help_checkin_journal_comment',
                      default=u'Describe, why you checkin the '
                      'selected documents'),
        required=False)


class CheckinCommentForm(form.Form):
    """Comment form for checkin procedure.
    """

    fields = field.Fields(ICheckinCommentFormSchema)
    ignoreContext = True
    label = _(u'heading_checkin_comment_form', u'Checkin Documents')

    @button.buttonAndHandler(_(u'button_checkin', default=u'Checkin'))
    def checkin_button_handler(self, action):
        """Handle checkin
        """

        data, errors = self.extractData()

        checkin_controller = MultiCheckinController(self.context, self.request)

        checkin_controller.checkin(self.get_document_paths(),
                                   comment=data['comment'])

        # redirect to dossier
        return self.request.RESPONSE.redirect(
            get_containg_document_tab_url(self.context))

    def get_document_paths(self):
        # from the form?
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value

        return get_document_paths(self.context, self.request)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        # on a document? go back to the document
        if IDocumentSchema.providedBy(self.context):
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        # otherwise to the dossier or task
        return get_containg_document_tab_url(self.context)

    def updateWidgets(self):
        super(CheckinCommentForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.get_document_paths())


class CheckinDocuments(layout.FormWrapper, grok.View):
    """View for checking in one or more documents. This view is either
    called from a tabbed_view or folder_contents action (using the
    request parameter "paths") or directly on the document itself
    (without any request parameters.)
    """

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('checkin_documents')
    form = CheckinCommentForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)

    def __call__(self, *args, **kwargs):
        try:
            return layout.FormWrapper.__call__(self, *args, **kwargs)
        except NoItemsSelected:
            msg = _(u'You have not selected any documents')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            return get_containg_document_tab_url(self.context)


class CheckinDocumentsWithoutComment(BrowserView):

    def __call__(self):
        checkin_controller = MultiCheckinController(self.context, self.request)
        checkin_controller.checkin(
            get_document_paths(self.context, self.request))

        # redirect to dossier
        return self.request.RESPONSE.redirect(
            get_containg_document_tab_url(self.context))
