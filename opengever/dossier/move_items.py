from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from OFS.CopySupport import CopyError, ResourceLockedError
from five import grok
from opengever.dossier import _
from plone.dexterity.interfaces import IDexterityContainer
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.z3cform import layout
from z3c.form import form, field
from z3c.form import validator
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IValidator
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import adapts
from zope.interface import Interface, Invalid, implements
from zope.schema.interfaces import IField
import z3c.form
from Products.statusmessages.interfaces import IStatusMessage
from opengever.dossier.behaviors.dossier import IDossierMarker


class IMoveItemsSchema(Interface):
    destination_folder = RelationChoice(
        title=_('label_destination', default="Destination"),
        description=_('help_destination',
                      default="Live Search: search the Plone Site"),
        source=ObjPathSourceBinder(
            object_provides=[
                'opengever.dossier.behaviors.dossier.IDossierMarker',
                'opengever.repository.repositoryfolder.IRepositoryFolderSchema']
            ),
        required=True,
        )
    #We Use TextLine here because Tuple and List have no hidden_mode.
    request_paths = schema.TextLine(title=u"request_paths")


class MoveItemsForm(form.Form):

    fields = field.Fields(IMoveItemsSchema)
    ignoreContext = True
    label = _('heading_move_items', default="Move Items")

    def updateWidgets(self):
        super(MoveItemsForm, self).updateWidgets()
        self.widgets['request_paths'].mode = HIDDEN_MODE
        value = self.request.get('paths')
        if value:
            self.widgets['request_paths'].value = ';;'.join(value)

    @z3c.form.button.buttonAndHandler(_(u'button_submit',
                                        default=u'Move'))
    def handle_submit(self, action):
        data, errors = self.extractData()

        if len(errors) == 0:
            root = getToolByName(self, 'portal_url')
            root = root.getPortalObject()
            source = data['request_paths'].split(';;')
            destination = data['destination_folder']
            sourceObjects = []
            failedObjects = []
            failedResourceLockedObjects = []
            copiedItems = 0

            # loop through paths
            for path in source:
                #get objects and parents
                sourceObjects.append(self.context.unrestrictedTraverse(
                        path.encode('utf-8')))
                sourceContainer = aq_parent(aq_inner(

                        self.context.unrestrictedTraverse(
                            path.encode('utf-8'))))
                #if parent isn't a dossier and obj is a document
                # it's connected to a task
                # and shouldn't be moved

                src_obj = sourceObjects[len(sourceObjects) - 1]
                is_doc = src_obj.portal_type == 'opengever.document.document'

                if not IDossierMarker.providedBy(sourceContainer) and is_doc:

                    name = sourceObjects[len(sourceObjects) - 1].title
                    msg = _(u'Document ${name} is connected to a Task.\
                    Please move the Task.', mapping=dict(name=name))
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    sourceObjects.remove(sourceObjects[len(sourceObjects) - 1])

            for obj in sourceObjects:
                sourceContainer = aq_parent(aq_inner(obj))
                #cut object and add it to clipboard
                try:
                    clipboard = sourceContainer.manage_cutObjects(obj.id)
                except ResourceLockedError:
                    failedResourceLockedObjects.append(obj.title)
                    continue

                try:
                    #try to paste object
                    destination.manage_pasteObjects(clipboard)
                    copiedItems += 1

                except ValueError:
                    #catch exception and add title to a list ofr failed objects
                    failedObjects.append(obj.title)

                except CopyError:
                    #catch exception and add title to a list of failed objects
                    failedObjects.append(obj.title)

            if copiedItems:
                msg = _(u'${copiedItems} Elements were moved successfully',
                        mapping=dict(copiedItems=copiedItems))
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='info')

            if failedObjects:
                msg = _(u'Failed to copy following objects: ${failedObjects}',
                        mapping=dict(failedObjects=','.join(failedObjects)))
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')

            if failedResourceLockedObjects:
                msg = _(u'Failed to copy following objects: ${failedObjects}\
                        . Locket via WebDAV',
                        mapping=dict(failedObjects=','.join(
                            failedResourceLockedObjects)))
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')

            self.request.RESPONSE.redirect(destination.absolute_url())

    @z3c.form.button.buttonAndHandler(_(u'button_cancel',
                                        default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class MoveItemsFormView(layout.FormWrapper, grok.View):
    """ The View wich display the SendDocument-Form.

    For sending documents with per mail.

    """

    grok.context(IDexterityContainer)
    grok.name('move_items')
    grok.require('zope2.View')
    form = MoveItemsForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)

    def render(self):
        if not self.request.get('paths') and not \
                self.form_instance.widgets['request_paths'].value:
            msg = _(u'You have not selected any items')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            # redirect to the right tabbedview_tab
            if self.request.form.get('orig_template'):

                return self.request.RESPONSE.redirect(
                    self.request.form.get('orig_template'))
            # fallback documents tab
            else:
                return self.request.RESPONSE.redirect(
                    '%s#documents' % self.context.absolute_url())

        return super(MoveItemsFormView, self).render()


class NotInContentTypes(Invalid):
    __doc__ = _(u"It isn't allowed to add such items there")


class DestinationValidator(validator.SimpleFieldValidator):
    implements(IValidator)
    adapts(Interface, Interface, Interface, IField, Interface)

    def validate(self, value):
        super(DestinationValidator, self).validate(value)
        source = self.view.widgets['request_paths'].value.split(';;')
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        sourceobjs = []
        for item in source:
            sourceobjs.append(portal_catalog(path={'query': item, 'depth': 0}))
        inContentTypes = False
        for item in value.allowedContentTypes():
            for sourceobj in sourceobjs:
                if sourceobj[0].portal_type in item.id:
                    inContentTypes = True
        if inContentTypes == False:
            raise NotInContentTypes(
                _(u"error_NotInContentTypes",
                  default=u"It isn't allowed to add such items there"))

validator.WidgetValidatorDiscriminators(
    DestinationValidator, field=IMoveItemsSchema['destination_folder'])
