from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.exceptions import NoItemsSelected
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.z3cform import layout
from z3c.form import form, field, button
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Interface


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

        if len(errors) == 0:
            # check in each document
            for obj in self.objects:
                if IDocumentSchema.providedBy(obj):
                    manager = getMultiAdapter((obj, obj.REQUEST),
                                              ICheckinCheckoutManager)

                    if not manager.is_checkin_allowed():
                        msg = _(u'Could not check in document ${title}',
                                mapping=dict(title=obj.Title()))
                        IStatusMessage(self.request).addStatusMessage(
                            msg, type='error')

                    else:
                        manager.checkin(data['comment'])
                        msg = _(u'Checked in: ${title}',
                                mapping=dict(title=obj.Title()))
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

            # redirect to dossier
            dossier = self.context
            while not IDossierMarker.providedBy(dossier):
                # move up
                dossier = aq_parent(aq_inner(dossier))
                if IPloneSiteRoot.providedBy(dossier):
                    raise Exception(
                        'Plone site reached - no dossier found')

            # check if the user has the permission to see it.
            portal_membership = getToolByName(
                self.context, 'portal_membership')
            if portal_membership.checkPermission('View', dossier):
                return self.request.RESPONSE.redirect(
                    '%s#documents' % dossier.absolute_url())
            else:
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        # on a document? go back to the document
        if IDocumentSchema.providedBy(self.context):
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        # otherwise go back to the dossier
        dossier = self.context
        while not IDossierMarker.providedBy(dossier):
            # move up
            dossier = aq_parent(aq_inner(dossier))
            if IPloneSiteRoot.providedBy(dossier):
                raise Exception(
                    'Plone site reached - no dossier found')

        return self.request.RESPONSE.redirect(
            '%s#documents' % dossier.absolute_url())

    @property
    def objects(self):
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
        return [lookup(p) for p in self.item_paths]

    @property
    def item_paths(self):
        # from the form?
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value

        # from folder_contents / tabbed_view?
        value = self.request.get('paths')
        if value:
            return value

        # from the context?
        if IDocumentSchema.providedBy(self.context):
            return ['/'.join(self.context.getPhysicalPath())]

        # nothing found..
        raise NoItemsSelected

    def updateWidgets(self):
        super(CheckinCommentForm, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.item_paths)


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

            # redirect to dossier
            dossier = self.context
            while not IDossierMarker.providedBy(dossier):
                # move up
                dossier = aq_parent(aq_inner(dossier))
                if IPloneSiteRoot.providedBy(dossier):
                    raise Exception(
                        'Plone site reached - no dossier found')

            return self.request.RESPONSE.redirect(
                '%s#documents' % dossier.absolute_url())
