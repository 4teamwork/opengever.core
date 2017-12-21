from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.exceptions import NoItemsSelected
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.tabbedview.utils import get_containing_document_tab_url
from plone import api
from plone.locking.interfaces import IRefreshableLockable
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface


class CheckinController(object):
    """Checks in one or multiple documents."""

    def __init__(self, request):
        self.portal = api.portal.get()
        self.request = request

    def checkin_document(self, document, comment=None):
        """Perform checkin for one document with an optional comment."""
        self.process_document(document, comment)

    def checkin_documents(self, document_paths, comment=None):
        """Perform checkin for multiple documents with an optional comment."""
        documents = self.resolve_documents(document_paths)
        for obj in documents:
            self.process_document(obj, comment)

    def resolve_documents(self, document_paths):
        if not document_paths:
            raise NoItemsSelected

        encoded_paths = [p.encode('utf-8') for p in document_paths]
        return [self.portal.unrestrictedTraverse(p) for p in encoded_paths]

    def process_document(self, obj, comment):
        if IDocumentSchema.providedBy(obj):
            self.perform_checkin(obj, comment)
        else:
            self.report_cannot_checkin_non_document(obj)

    def perform_checkin(self, document, comment):
        manager = getMultiAdapter(
            (document, self.request),
            ICheckinCheckoutManager,
            )

        if not manager.is_checkin_allowed():
            msg = _(
                u'Could not check in document ${title}',
                mapping=dict(title=document.Title().decode('utf-8')),
                )
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')

        else:
            manager.checkin(comment)
            msg = _(
                u'Checked in: ${title}',
                mapping=dict(title=document.Title().decode('utf-8')))
            IStatusMessage(self.request).addStatusMessage(msg, type=u'info')

    def report_cannot_checkin_non_document(self, obj):
        title = obj.Title()
        if not isinstance(title, unicode):
            title = title.decode('utf-8')
        msg = _(
            u'Could not check in ${title}, it is not a document.',
            mapping=dict(title=title))
        IStatusMessage(self.request).addStatusMessage(msg, type=u'error')


class IContextCheckinCommentSchema(Interface):
    """Form schema to enter a journal comment for checkin."""

    comment = schema.Text(
        title=_(
            u'label_checkin_journal_comment',
            default=u'Journal Comment',
            ),
        description=_(
            u'help_checkin_journal_comment',
            default=u'Describe, why you checkin the selected documents',
            ),
        required=False,
        )


class CheckinContextCommentForm(form.Form):
    """Form to checkin one document, the form's context."""

    fields = field.Fields(IContextCheckinCommentSchema)
    ignoreContext = True
    label = _(u'heading_checkin_comment_form', u'Checkin Documents')

    def __init__(self, context, request):
        super(CheckinContextCommentForm, self).__init__(context, request)
        self.locked = IRefreshableLockable(self.context).locked()
        if self.locked:
            # Add a warning onto a locked document checkin view
            msg = _(
                u'label_warn_checkout_locked',
                default=u' '.join((
                    'This document is currently being worked on.',
                    'When you check it in manually you will lose the changes.',
                    'Please allow for the process to be finished first.'
                    )),
                )
            IStatusMessage(self.request).addStatusMessage(msg, type=u'warning')

            # Swap the button label out on a locked document
            for form_button in self.buttons.items():
                if form_button[0] == 'button_checkin':
                    button_payload = form_button[1]
                    button_payload.title = _(
                        u'button_checkin_anyway',
                        default=u'Checkin anyway'
                        )
                    form_button = (
                        'button_checkin_anyway',
                        button_payload,
                        )

        self.checkin_controller = CheckinController(self.request)

    @button.buttonAndHandler(_(u'button_checkin', default=u'Checkin'))
    def checkin_button_handler(self, action):
        # Errors are handled by the checkin
        data = self.extractData()[0]

        self.checkin_controller.checkin_document(
            self.context,
            comment=data['comment'],
            )

        return self.redirect()

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class IPathsCheckinCommentSchema(IContextCheckinCommentSchema):
    """Contains an additional (hidden) paths field."""

    paths = schema.TextLine(title=u'Selected Items')


class CheckinPathsCommentForm(CheckinContextCommentForm):
    """Form to checkin multiple documents, based on their path."""

    fields = field.Fields(IPathsCheckinCommentSchema)

    @button.buttonAndHandler(_(u'button_checkin', default=u'Checkin'))
    def checkin_button_handler(self, action):
        # Errors are handled by the checkin
        data = self.extractData()[0]

        self.checkin_controller.checkin_documents(
            self.get_document_paths(),
            comment=data['comment'],
            )

        return self.redirect()

    def get_document_paths(self):
        """Return document paths from previously submitted plone form form
        request or initialize from the submitted checkbox list.
        """
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            return value.split(';;')
        return self.request.get('paths', [])

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(
            get_containing_document_tab_url(self.context))

    def updateWidgets(self):
        super(CheckinPathsCommentForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.get_document_paths())


class CheckinDocument(layout.FormWrapper):
    """Checkin one document (context) with comment."""

    form = CheckinContextCommentForm


class CheckinDocuments(layout.FormWrapper):
    """Checkin multiple documents with comment.

    This view is called from a tabbed_view.
    """

    form = CheckinPathsCommentForm

    def __call__(self, *args, **kwargs):
        try:
            return layout.FormWrapper.__call__(self, *args, **kwargs)
        except NoItemsSelected:
            msg = _(u'You have not selected any documents.')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')

            return self.request.RESPONSE.redirect(
                get_containing_document_tab_url(self.context))


class CheckinDocumentWithoutComment(BrowserView):
    """Checkin one document (context) without comment."""

    def __init__(self, context, request):
        super(CheckinDocumentWithoutComment, self).__init__(context, request)
        self.checkin_controller = CheckinController(self.request)

    def __call__(self):
        self.checkin()
        return self.redirect()

    def checkin(self):
        self.checkin_controller.checkin_document(self.context)

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class CheckinDocumentsWithoutComment(CheckinDocumentWithoutComment):
    """Checkin multiple documents without comment.

    This view is called from a tabbed_view.
    """

    def checkin(self):
        try:
            self.checkin_controller.checkin_documents(
                self.request.get('paths'),
                )
        except NoItemsSelected:
            msg = _(u'You have not selected any documents.')
            IStatusMessage(self.request).addStatusMessage(msg, type=u'error')

            return self.request.RESPONSE.redirect(
                get_containing_document_tab_url(self.context))

    def redirect(self):
        return self.request.RESPONSE.redirect(
            get_containing_document_tab_url(self.context))
