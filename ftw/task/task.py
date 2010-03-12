from five import grok
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import implements, Interface
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPage
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zc.relation.interfaces import ICatalog

from five import grok

from Acquisition import aq_parent, aq_inner
from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from datetime import datetime, timedelta
from rwproperty import getproperty, setproperty
from plone.registry.interfaces import IRegistry
from ftw.task.interfaces import ITaskSettings
from plone.app.layout.viewlets import content
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.formwidget import autocomplete
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.indexer import indexer
from plone.z3cform.traversal import WidgetTraversal
from plone.app.dexterity.behaviors.related import IRelatedItems
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.content import Container
from plone.directives import form, dexterity
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

from ftw.task import util
from ftw.task import _
from ftw.task.interfaces import ITaskSettings

from opengever.base.interfaces import ISequenceNumber
from opengever.translations.browser.add import TranslatedAddForm
from opengever.octopus.tentacle.interfaces import IContactInformation


class ITask(form.Schema):

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'title',
            u'issuer',
            u'task_type',
            u'responsible',
            u'deadline',
            u'text',
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
            u'date_of_completion',
            ],
        )


    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required = True,
    )

    form.widget(issuer=AutocompleteFieldWidget)
    issuer = schema.Choice(
        title =_(u"label_issuer", default=u"Issuer"),
        description = _('help_issuer', default=u""),
        vocabulary = 'opengever.octopus.tentacle.contacts.ContactsVocabularyFactory',
        required = True,
        )

    form.widget(task_type='z3c.form.browser.radio.RadioFieldWidget')
    task_type = schema.Choice(
        title =_(u'label_task_type', default=u'Task Type'),
        description = _('help_task_type', default=u''), 
        required = True,
        readonly = False,
        default = None,
        missing_value = None,
        source = util.getTaskTypeVocabulary,
    )
    
    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default=""),
        vocabulary = 'opengever.octopus.tentacle.contacts.UsersVocabularyFactory',
        required = True,
        )

    form.widget(deadline='ftw.datepicker.widget.DatePickerFieldWidget')
    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required = True,
        )

    form.widget(date_of_completion='ftw.datepicker.widget.DatePickerFieldWidget')
    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required = False,
        )

    form.primary('text')
    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required = False,
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

    form.order_before(**{'ITransition.transition': "responsible"})

# # XXX doesn't work yet.
#@form.default_value(field=ITask['issuer'])

def default_issuer(data):
    portal_state = getMultiAdapter(
        (data.context, data.request),
        name=u"plone_portal_state")
    member = portal_state.member()
    return member.getId()


from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.autoform.interfaces import ORDER_KEY
# move relatedItems to default fieldset
# by removing it from categorization fieldset
IRelatedItems.setTaggedValue(FIELDSETS_KEY, [])

# # # IRelatedItems.setTaggedValue( FIELDSETS_KEY, [
#         Fieldset( 'common', fields=[
#                 'relatedItems',
#                 ])
#         ] )
#

IRelatedItems.setTaggedValue(ORDER_KEY, [('relatedItems', 'after', 'text')])


#ITransition.setTaggedValue(FIELDSETS_KEY, [])
#ITransition.setTaggedValue(ORDER_KEY, [('transition', 'before', 'responsible')])

@grok.subscribe(ITask, IObjectCreatedEvent)
def setID(task, event):
    task.id = "task-%s" % getUtility(ISequenceNumber).get_number(task)
    nr = getUtility(ISequenceNumber).get_number(task)
    task._sequence_number = nr


class Task(Container):
    implements(ITask)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    # REMOVED UNCOMMENT unused title function
    # def Title(self):
    #     registry = queryUtility(IRegistry)
    #     proxy = registry.forInterface(ITaskSettings)
    #     title = "#%s %s"% (getUtility(ISequenceNumber).get_number(self),self.task_type)
    #     relatedItems = getattr(self,'relatedItems',[])
    #     if len(relatedItems) == 1:
    #         title += " (%s)" % self.relatedItems[0].to_object.title
    #     elif len(relatedItems) > 1:
    #         title += " (%i Dokumente)" % len(self.relatedItems)
    #     if self.text:
    #         crop_length = int(getattr(proxy,'crop_length',20))
    #         text = self.text.encode('utf8')
    #         text = self.restrictedTraverse('@@plone').cropText(text,crop_length)
    #         text = text.decode('utf8')
    #         title += ": %s" % text
    #     return title

    @property
    def sequence_number(self):
        return self._sequence_number
        
    @property
    def task_type_category(self):
        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(ITaskSettings)
        if self.task_type in reg_proxy.task_types_uni_ref:
            return u'uni_ref'
        elif self.task_type in reg_proxy.task_types_uni_val:
            return u'uni_val'
        elif self.task_type in reg_proxy.task_types_bi_ref:
            return u'bi_ref'
        elif self.task_type in reg_proxy.task_types_bi_val:
            return u'bi_val'
        return None


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

    def getContainingTask(self):
        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == self.context.portal_type:
            return [parent,]
        return None
    
    def getSubDocuments(self):
        brains = self.context.getFolderContents(full_objects=False,
                                               contentFilter={'portal_type': 'opengever.document.document'})

        docs = []
        for doc in brains:
            docs.append(doc.getObject())

        for rel in self.context.relatedItems:
            docs.append(rel.to_object)
        docs.sort(lambda x, y: cmp(x.Title(), y.Title()))
        return docs
    
    def responsible_link(self):
        info = getUtility(IContactInformation)
        task = ITask(self.context)
        return info.render_link(task.responsible)

    def issuer_link(self):
        info = getUtility(IContactInformation)
        task = ITask(self.context)
        return info.render_link(task.issuer)


# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.

#class AddForm(dexterity.AddForm):

class AddForm(TranslatedAddForm):
    grok.name('ftw.task.task')

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            utool = getToolByName(self.context, 'portal_url')
            portal_path = utool.getPortalPath()
            # paths have to be relative to the portal
            paths = [path[len(portal_path):] for path in paths]
            self.request.set('form.widgets.IRelatedItems.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
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
        if 1:
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


class Byline(grok.Viewlet, content.DocumentBylineViewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(ITask)
    grok.name('plone.belowcontenttitle.documentbyline')

    update = content.DocumentBylineViewlet.update

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    def responsible_link(self):
        info = getUtility(IContactInformation)
        task = ITask(self.context)
        return info.render_link(task.responsible)


@indexer(ITask)
def related_items( obj ):
    catalog = getUtility( ICatalog )
    intids = getUtility( IIntIds )
    obj_id = intids.getId( obj )
    results = []
    relations = catalog.findRelations({'from_attribute': 'relatedItems'})
    for rel in relations:
        results.append(rel.to_id)
    return results
grok.global_adapter(related_items, name='related_items')


@indexer(ITask)
def date_of_completion(obj):
    # handle 'None' dates. we always need a date for indexing.
    if obj.date_of_completion is None:
        return datetime(1970, 1, 1)
    return obj.date_of_completion
grok.global_adapter(date_of_completion, name='date_of_completion')


@indexer(ITask)
def assigned_client(obj):
    #set the client_id of the home mandant of the respectively responsible user
    if obj.responsible is not None:
        info = getUtility(IContactInformation)
        user = info.get_user_by_id(obj.responsible)
        return user.get('client', None)
grok.global_adapter(assigned_client, name='assigned_client')
