from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
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


class DestinationPathSourceBinder(ObjPathSourceBinder):

    def __call__(self, context):
        return self.path_source(
            context,
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)


class IMoveItemsSchema(Interface):
    destination_folder = RelationChoice(
        title=_('intern_receiver', default="Intern receiver"),
        description=_('help_intern_receiver',
                      default="Live Search: search for users and contacts"),
        source= DestinationPathSourceBinder(),
        required=True,
        )

    request_paths = schema.TextLine(title=u"request_paths")


class MoveItemsForm(form.Form):

    fields = field.Fields(IMoveItemsSchema)
    ignoreContext = True
    label = _('heading_move_items', default="Move Items")

    def updateWidgets(self):
        super(MoveItemsForm, self).updateWidgets()
        self.widgets['request_paths'].mode = HIDDEN_MODE
        value = self.item_paths
        if value:
            self.widgets['request_paths'].value = ';;'.join(value)

    @property
    def item_paths(self):
        field_name = self.prefix + self.widgets.prefix + 'request_paths'
        value = self.request.get(field_name, False)
        if value:
            value = value.split(';;')
            return value
        value = self.request.get('paths')
        if not value:
            pass
        return value

    @z3c.form.button.buttonAndHandler(_(u'button_submit',
                                        default=u'Move'))
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) == 0:
            root = getToolByName(self, 'portal_url')
            root = root.getPortalObject()
            source = data['request_paths']
            destination = data['destination_folder']
            sourceObject = self.context.unrestrictedTraverse(
                source.encode('utf-8'))
            sourceContainer = aq_parent(aq_inner(sourceObject))
            clipboard = sourceContainer.manage_cutObjects(sourceObject.id)
            destination.manage_pasteObjects(clipboard)
            self.request.RESPONSE.redirect(destination.absolute_url())

    @z3c.form.button.buttonAndHandler(_(u'button_cancel',
                                        default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class MoveItemsFormView(layout.FormWrapper, grok.CodeView):
    """ The View wich display the SendDocument-Form.

    For sending documents with per mail.

    """

    grok.context(IDexterityContainer)
    grok.name('move_items')
    grok.require('zope2.View')
    form = MoveItemsForm

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)


class NotInContentTypes(Invalid):
    __doc__ = _(u"It isn't allowed to add such items there")


class DestinationValidator(validator.SimpleFieldValidator):
    implements(IValidator)
    adapts(Interface, Interface, Interface, IField, Interface)

    def validate(self, value):
        super(DestinationValidator, self).validate(value)
        source = self.view.widgets['request_paths'].value
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        sourceobj = portal_catalog(path={'query': source, 'depth': 0})
        inContentTypes = False
        for item in value.allowedContentTypes():
            if sourceobj[0].portal_type in item.portal_type:
                inContentTypes = True
            if inContentTypes == False:
                raise NotInContentTypes(
                    _(u"error_NotInContentTypes",
                      default=u"It isn't allowed to add such items there"))

validator.WidgetValidatorDiscriminators(
    DestinationValidator, field=IMoveItemsSchema['destination_folder'])
