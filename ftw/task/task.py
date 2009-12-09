from five import grok
from zope import schema
from zope.interface import implements, Interface
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPage
from zope.component import queryMultiAdapter, getUtility, getMultiAdapter
from zope.app.container.interfaces import IObjectAddedEvent

from Acquisition import aq_parent, aq_inner
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from datetime import datetime, timedelta

from plone.formwidget import autocomplete
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform.traversal import WidgetTraversal
from plone.app.dexterity.behaviors.related import IRelatedItems
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.content import Container
from plone.directives import form, dexterity

from ftw.task import util
from ftw.task import _


class ITask(form.Schema):

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'title',
            u'issuer',
            u'responsible',
            u'text',
            u'deadline',
            ],
        )

    form.fieldset(
        u'additional',
        label = _(u'fieldset_additional', u'Additional'),
        fields = [
            u'expectedStartOfWork',
            u'expectedDuration',
            u'expectedCost',
            u'effectiveDuration',
            u'effectiveCost',
        ],
    )

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required = True,
    )

    issuer = schema.TextLine(
        title =_(u"label_issuer", default=u"Issuer"),
        description = _('help_issuer', default=u""),
    )

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default=""),
        source = util.getManagersVocab,
        required = False,
    )

    form.primary('text')
    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required = True,
    )

    form.widget(deadline='ftw.datepicker.widget.DatePickerFieldWidget')
    deadline = schema.Date(
        title=_(u"label_deadline", default=u""),
        description=_(u"help_deadline", default=u"Deadline"),
        required = True,
    )

    form.widget(
    expectedStartOfWork='ftw.datepicker.widget.DatePickerFieldWidget')
    expectedStartOfWork = schema.Date(
        title =_(u"label_expectedStartOfWork", default="Start with work"),
        description = _(u"help_expectedStartOfWork", default=""),
        required = False,
    )

    expectedDuration = schema.Float(
        title = _(u"label_expectedDuration", default="Expected duration", ),
        description = _(u"help_expectedDuration", default="", ),
        required = False,
    )

    expectedCost = schema.Int(
        title = _(u"label_expectedCost", default="expected cost"),
        description = _(u"help_expectedCost", default=""),
        required = False,
    )

    effectiveDuration = schema.Float(
        title = _(u"label_effectiveDuration", default="effective duration"),
        description = _(u"help_effectiveDuration", default=""),
        required = False,
    )

    effectiveCost = schema.Int(
        title=_(u"label_effectiveCost", default="effective cost"),
        description=_(u"help_effectiveCost", default=""),
        required = False,
    )


@form.default_value(field=ITask['issuer'])
def default_issuer(data):
    portal_state = getMultiAdapter(
        (data.context, data.request),
        name=u"plone_portal_state")
    member = portal_state.member()
    return member.getProperty('fullname') or member.getId()


from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.autoform.interfaces import ORDER_KEY
# move relatedItems to default fieldset
# by removing it from categorization fieldset
IRelatedItems.setTaggedValue(FIELDSETS_KEY, [])
# IRelatedItems.setTaggedValue( FIELDSETS_KEY, [
#         Fieldset( 'common', fields=[
#                 'relatedItems',
#                 ])
#         ] )
IRelatedItems.setTaggedValue(ORDER_KEY, [('relatedItems', 'before', 'text')])


@grok.subscribe(ITask, IObjectAddedEvent)
def setID(task, event):
    task._sequence_number = util.create_sequence_number(task)


class Task(Container):
    implements(ITask)

    @property
    def sequence_number(self):
        return self._sequence_number


@form.default_value(field=ITask['deadline'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return datetime.today() + timedelta(5)


class ITaskView(Interface):
    pass


class View(dexterity.DisplayForm):
    implements(ITaskView)
    grok.context(ITask)
    grok.require('zope2.View')

    def getSubTasks(self):
        tasks = self.context.getFolderContents(full_objects=False,
            contentFilter={'portal_type': 'ftw.task.task'})
        return tasks

    def getResponses(self):
        responses = self.context.getFolderContents(full_objects=True,
        contentFilter={'portal_type': 'ftw.task.response'})
        return responses


# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.

class AddForm(dexterity.AddForm):
    grok.name('ftw.task.task')

    def update(self):
        paths = self.request.get('paths', [])
        if paths:
            utool = getToolByName(self.context, 'portal_url')
            portal_path = utool.getPortalPath()
            # paths have to be relative to the portal
            paths = [path[len(portal_path):] for path in paths]
            self.request.set('form.widgets.IRelatedItems.relatedItems', paths)
        super(AddForm, self).update()


class TaskWidgetTraversal(WidgetTraversal):
    implements(ITraversable)

    def __init__(self, context, request = None):
        self.request = request

        if not ITask.providedBy(context):
            context = aq_parent(aq_inner(context))
        fti = getUtility(IDexterityFTI, name='ftw.task.task')
        adder = queryMultiAdapter((context, self.request, fti),
                              IBrowserPage)

        self.context = adder


grok.global_adapter(TaskWidgetTraversal,
    ((ITask, IBrowserRequest)),
    ITraversable,
    name=u"widget",
    )
grok.global_adapter(TaskWidgetTraversal,
    ((ITaskView, IBrowserRequest)),
    ITraversable,
    name=u"widget",
    )


class TaskAutoCompleteSearch(grok.CodeView, autocomplete.widget.AutocompleteSearch):
    grok.context(autocomplete.interfaces.IAutocompleteWidget)
    grok.name("autocomplete-search")

    def __call__(self):
        return autocomplete.widget.AutocompleteSearch.__call__(self)

    def validate_access(self):
        content = self.context.form.context
        super_method = autocomplete.widget.AutocompleteSearch.validate_access
        if not ITask.providedBy(content):
            # not on a task
            return super_method(self)
        view_name = self.request.getURL().split('/')[-3]
        if view_name in ['edit', 'add', '@@edit'] or view_name.startswith('++add++'):
            # edit task itself
            return super_method(self)
        # add response to the task
        # XXX
        return
        view_name = '++add++ftw.task.task'
        view_instance = content.restrictedTraverse(view_name)
        getSecurityManager().validate(content,
            content,
            view_name,
            view_instance,
        )

    def render(self):
        pass
