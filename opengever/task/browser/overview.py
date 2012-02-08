from Acquisition import aq_parent, aq_inner
from five import grok
from opengever.ogds.base.utils import get_client_id
from opengever.base.browser.helper import client_title_helper
from opengever.base.browser.helper import css_class_from_brain, css_class_from_obj
from opengever.globalindex.utils import indexed_task_link
from opengever.globalindex.model.task import Task
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from plone.directives.dexterity import DisplayForm
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.interfaces import ICatalogBrain
from z3c.form.field import Field
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.interfaces import IContextAware, IField
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


def get_field_widget(obj, field):
    """Returns the field widget of a field in display mode without
    touching any form.
    The `field` should be a z3c form field, not a zope schema field.

    copied from collective.dexteritytextindexer
    """
    assert IField.providedBy(field), 'field is not a form field'

    if field.widgetFactory.get(DISPLAY_MODE) is not None:
        factory = field.widgetFactory.get(DISPLAY_MODE)
        widget = factory(field.field, obj.REQUEST)
    else:
        widget = getMultiAdapter(
            (field.field, obj.REQUEST), IFieldWidget)
    widget.name = '' + field.__name__  # prefix not needed
    widget.id = widget.name.replace('.', '-')
    widget.context = obj
    alsoProvides(widget, IContextAware)
    widget.mode = DISPLAY_MODE
    widget.ignoreRequest = True
    widget.update()
    return widget


class IssuerWidget(object):
    """ Widget to display the issuer
    """
    implements(IFieldWidget)

    def __init__(self, context):
        self.context = context
        self.label = _('label_issuer')

    def render(self):
        """ Render the issuer of the current task as link.
        """
        info = getUtility(IContactInformation)
        task = ITask(self.context)

        if task.predecessor:
            client_id = task.predecessor.split(':')[0]
        else:
            client_id = get_client_id()

        client = client_title_helper(task, client_id)

        return client + ' / ' + info.render_link(task.issuer)

    def label(self):
        return self.label


class ResponsibleWidget(object):
    """ Widget to display the responsible
    """
    implements(IFieldWidget)

    def __init__(self, context):
        self.context = context
        self.label = _('label_responsible')

    def render(self):
        """ Render the responsible of the current task as link.
        """
        info = getUtility(IContactInformation)
        task = ITask(self.context)
        if not len(task.widgets.responsible_client):
            # in some special cases the responsible client may not be set.
            return info.render_link(task.responsible)

        if len(info.get_clients()) <= 1:
            # We have a single client setup, so we don't need to display
            # the client here.
            return info.render_link(task.responsible)

        client = client_title_helper(task, task.widgets.responsible_client)

        return client + ' / ' + info.render_link(task.responsible)

    def label(self):
        return self.label

class StateWidget(object):
    """ Widget to display the state
    """
    implements(IFieldWidget)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.label = _('label_workflow_state')

    def get_state(self):
        return getToolByName(self.context, 'portal_workflow').getInfoFor(
            self.context, 'review_state')

    def get_translated_state(self):
        return translate(
            self.get_state(),
            domain='plone',
            context=self.request)

    def render(self):
        return "<span class=wf-%s>%s</span>" % (
            self.get_state(),
            self.get_translated_state(),
        )

    def label(self):
        return self.label


class Overview(DisplayForm, OpengeverTab):
    grok.context(ITask)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def catalog(self, types, showTrashed=False, depth=2):
        return self.context.portal_catalog(
            portal_type=types,
            path=dict(depth=depth,
                query='/'.join(self.context.getPhysicalPath())),
            sort_on='modified',
            sort_order='reverse')

    def get_type(self, item):
        """differ the object typ and return the type as string
        """
        if not item:
            return None
        elif IFieldWidget.providedBy(item):
            return 'widget'
        elif isinstance(item, dict):
            return 'dict'
        elif ICatalogBrain.providedBy(item):
            return 'brain'
        elif isinstance(item, Task):
            return 'sqlalchemy_object'
        else:
            return 'obj'

    def boxes(self):
        items = [
            [
            dict(
                id='additional_attributes',
                content=self.additional_attributes()),
             dict(id='documents', content=self.documents()),],

            [dict(id='containing_task', content=self.get_containing_task()),
             dict(id='sub_task', content=self.get_sub_tasks()),
             dict(id='predecessor_task', content=self.get_predecessor_task()),
             dict(id='successor_tasks', content=self.get_successor_tasks()),
            ],
            ]

        return items

    def documents(self):
        """ Return documents and related documents
        """
        # Documents
        documents = self.catalog(
            ['opengever.document.document', 'ftw.mail.mail', ])
        document_list = [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': document.document_date and \
                document.document_date.strftime('%d.%m.%Y') or '',
            'css_class': self.get_css_class(document),
            'portal_type': document.portal_type,
        } for document in documents]

        # Related documents
        for item in self.context.relatedItems:
            obj = item.to_object
            if (obj.portal_type == 'opengever.document.document'\
                    or obj.portal_type == 'ftw.mail.mail'):
                document_list.append(obj)

        return document_list

    def additional_attributes(self):
        """ Attributes to display
        """
        items = []
        attributes_to_display = [
            'title',
            'text',
            'task_type',
            'state',
            'deadline',
            'issuer',
            'responsible',
        ]

        for attr in attributes_to_display:
            if attr == 'state':
                items.append(StateWidget(self.context, self.request))
            elif attr == 'issuer':
                items.append(IssuerWidget(self.context))
            elif attr == 'responsible':
                items.append(ResponsibleWidget(self.context))
            else:
                field = ITask.get(attr)
                field = Field(field, interface=field.interface,
                       prefix='')

                items.append(get_field_widget(self.context, field))

        return items

    def get_css_class(self, item, is_brain=True):
        """Return the css classes
        """
        if is_brain:
            css = css_class_from_brain(item)
        else:
            css = css_class_from_obj(item)

        return "%s %s" % ("rollover-breadcrumb", css)

    def get_review_state_css(self, obj):
        """ Return the css class for the reviewstate
        """
        if not ITask.providedBy(obj):
            return None

        state = getToolByName(self.context, 'portal_workflow').getInfoFor(
            obj, 'review_state')

        return 'wf-%s' % state

    def get_sub_tasks(self):
        """ Return the subtasks
        """
        tasks = self.context.getFolderContents(
            contentFilter={'portal_type': 'opengever.task.task'})
        return [task for task in tasks]

    def get_containing_task(self):
        """ Get the parent-tasks if we have one
        """
        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == self.context.portal_type:
            return [parent]
        return []

    def subtask_responsible(self, subtask):
        """ Render the responsible of a subtask (object) as text.
        """

        if not ITask.providedBy(subtask) and \
                subtask.portal_type != 'opengever.task.task':
            # It is not a task, it may be a document or something else. So
            # we do nothing.
            return None

        info = getUtility(IContactInformation)

        if not subtask.responsible_client or len(info.get_clients()) <= 1:
            # No responsible client is set yet or we have a single client
            # setup.
            return info.describe(subtask.responsible)

        else:
            client = client_title_helper(subtask, subtask.responsible_client)
            return client + ' / ' + info.describe(subtask.responsible)

    def get_predecessor_task(self):
        """ Get the original task
        """
        controller = ISuccessorTaskController(self.context)
        task = controller.get_predecessor()
        # box rendering need a list
        if not task:
            return []
        return [task]

    def get_successor_tasks(self):
        """ Get the task from which this task was copied
        """
        controller = ISuccessorTaskController(self.context)
        return controller.get_successors()

    def render_indexed_task(self, item, display_client=True):
        """ Render the link for a globalindex sqlalchemy object
        """
        return indexed_task_link(item, display_client)
