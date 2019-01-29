from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.CopySupport import CopyError, ResourceLockedError
from opengever.base.source import RepositoryPathSourceBinder
from opengever.base.source import SolrObjPathSourceBinder
from opengever.document.document import IDocumentSchema
from opengever.dossier import _
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.globalindex.model.task import Task
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import form, field
from z3c.form import validator
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface, Invalid
import z3c.form


class IMoveItemsSchema(Interface):
    destination_folder = RelationChoice(
        title=_('label_destination', default="Destination"),
        description=_('help_destination',
                      default="Live Search: search the Plone Site"),
        source=RepositoryPathSourceBinder(
            object_provides=[
                'opengever.dossier.behaviors.dossier.IDossierMarker',
                'opengever.repository.repositoryfolder.IRepositoryFolderSchema'
                ],
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                ],
                'review_state': DOSSIER_STATES_OPEN + [
                    'repositoryfolder-state-active',
                    'repositoryroot-state-active']
                },
            review_state=DOSSIER_STATES_OPEN + [
                'repositoryfolder-state-active',
                'repositoryroot-state-active',
            ],
            ),
        required=True,
        )
    # We Use TextLine here because Tuple and List have no hidden_mode.
    request_paths = schema.TextLine(title=u"request_paths")


class IMoveTemplateItemsSchema(IMoveItemsSchema):
    destination_folder = RelationChoice(
        title=_('label_destination', default="Destination"),
        description=_('help_destination',
                      default="Live Search: search the Plone Site"),
        source=SolrObjPathSourceBinder(
            navigation_tree_query={
                'object_provides': [
                    ITemplateFolder.__identifier__,
                    IDossierTemplateMarker.__identifier__,
                    ]}
            ),
        required=True,
        )


class MoveItemsForm(form.Form):

    fields = field.Fields(IMoveItemsSchema)
    ignoreContext = True
    label = _('heading_move_items', default="Move Items")

    def updateWidgets(self):
        super(MoveItemsForm, self).updateWidgets()
        self.widgets['request_paths'].mode = HIDDEN_MODE

        paths = self.request.get('paths')
        if paths:
            self.widgets['request_paths'].value = ';;'.join(paths)

        task_ids = self.request.get('task_ids')
        if task_ids:
            paths = []
            for task in Task.query.by_ids(task_ids):
                paths.append(task.physical_path)

            self.widgets['request_paths'].value = ';;'.join(paths)

    @z3c.form.button.buttonAndHandler(_(u'button_submit',
                                        default=u'Move'))
    def handle_submit(self, action):
        data, errors = self.extractData()
        if len(errors) == 0:

            destination = data['destination_folder']
            failed_objects = []
            failed_resource_locked_objects = []
            copied_items = 0

            try:
                objs = self.extract_selected_objs(data)
            except KeyError:
                IStatusMessage(self.request).addStatusMessage(
                    _(u"The selected objects can't be found, please try it again."),
                    type='error')
                return self.request.RESPONSE.redirect(self.context.absolute_url())

            for obj in objs:
                parent = aq_parent(aq_inner(obj))

                if IDocumentSchema.providedBy(obj) and not obj.is_movable():
                    if obj.is_inside_a_task():
                        msg = _(
                            'label_not_movable_since_inside_task',
                            default=u'Document ${name} is inside a task and '
                                    u'therefore not movable. Move the task '
                                    u'instead',
                            mapping=dict(name=obj.title))
                    elif obj.is_inside_a_proposal():
                        msg = _(
                            'label_not_movable_since_inside_proposal',
                            default=u'Document ${name} is inside a proposal '
                                    u'and therefore not movable. Move the '
                                    u'proposal instead',
                            mapping=dict(name=obj.title))
                    else:
                        raise Exception(
                            'Failed to determine the reason for unmovable document. '
                            'Did IDocumentSchema.is_moveable change?'
                        )
                    IStatusMessage(self.request).addStatusMessage(msg, type='error')
                    continue

                try:
                    # Try to cut and paste object
                    clipboard = parent.manage_cutObjects(obj.id)
                    destination.manage_pasteObjects(clipboard)
                    copied_items += 1

                except ResourceLockedError:
                    # The object is locket over webdav
                    failed_resource_locked_objects.append(obj.title)
                    continue

                except (ValueError, CopyError):
                    # Catch exception and add title to a list of failed objects
                    failed_objects.append(obj.title)
                    continue

            self.create_statusmessages(
                copied_items,
                failed_objects,
                failed_resource_locked_objects, )

            self.request.RESPONSE.redirect(destination.absolute_url())

    @z3c.form.button.buttonAndHandler(_(u'button_cancel',
                                        default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def extract_selected_objs(self, data):
        paths = data['request_paths'].split(';;')
        objs = []

        for path in paths:
            objs.append(
                self.context.unrestrictedTraverse(path.encode('utf-8')))

        return objs

    def create_statusmessages(
        self,
        copied_items,
        failed_objects,
        failed_resource_locked_objects, ):
        """ Create statusmessages with errors and infos af the move-process
        """
        if copied_items:
            msg = _(u'${copied_items} Elements were moved successfully',
                    mapping=dict(copied_items=copied_items))
            IStatusMessage(self.request).addStatusMessage(
                msg, type='info')

        if failed_objects:
            msg = _(u'Failed to copy following objects: ${failed_objects}',
                    mapping=dict(failed_objects=','.join(failed_objects)))
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

        if failed_resource_locked_objects:
            msg = _(u'Failed to copy following objects: ${failed_objects}. '
                    u'Locked via WebDAV',
                    mapping=dict(failed_objects=','.join(
                        failed_resource_locked_objects)))
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')


class MoveTemplateItemsForm(MoveItemsForm):
    fields = field.Fields(IMoveTemplateItemsSchema)


class MoveItemsFormView(layout.FormWrapper):
    """ View to move selected items into another location
    """

    form = MoveItemsForm

    def __init__(self, context, request):
        if self.within_template_folder(context):
            self.form = MoveTemplateItemsForm

        super(MoveItemsFormView, self).__init__(context, request)

    def assert_valid_container_state(self):
        container = self.context
        if not self.within_template_folder(container) and \
                IDossierMarker.providedBy(container) and not container.is_open():
            msg = _(u'Can only move objects from open dossiers!')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            self.request.RESPONSE.redirect(
                '%s#documents' % container.absolute_url())

    def render(self):
        self.assert_valid_container_state()
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

    def within_template_folder(self, context):
        """ This method checks if the current context is within a templatefolder.
        """
        return bool(filter(ITemplateFolder.providedBy, aq_chain(context)))


class NotInContentTypes(Invalid):
    __doc__ = _(u"It isn't allowed to add such items there.")


class DestinationValidator(validator.SimpleFieldValidator):
    """Validator for destination-path.
    We check the destinations allowed content-type. If one or more source-types
    are not allowed in the destination, we raise an error
    """

    def validate(self, value):
        super(DestinationValidator, self).validate(value)

        # Allowed contenttypes for destination-folder
        allowed_types = [t.getId() for t in value.allowedContentTypes()]

        # Paths to source object
        source = self.view.widgets['request_paths'].value.split(';;')

        # Get source-brains
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        src_brains = portal_catalog(path={'query': source, 'depth': 0})
        failed_objects = []

        # Look for invalid contenttype
        for src_brain in src_brains:
            if src_brain.portal_type not in allowed_types:
                failed_objects.append(src_brain.Title.decode('utf8'))

        # If we found one or more invalid contenttypes, we raise an error
        if failed_objects:
            raise NotInContentTypes(
                _(u"error_NotInContentTypes ${failed_objects}",
                  default=u"It isn't allowed to add such items there: "
                          "${failed_objects}", mapping=dict(
                              failed_objects=', '.join(failed_objects))))


validator.WidgetValidatorDiscriminators(
    DestinationValidator, field=IMoveItemsSchema['destination_folder'])
