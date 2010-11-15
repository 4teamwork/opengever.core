from AccessControl import getSecurityManager
from opengever.globalindex.utils import indexed_task_link
from zope.schema.vocabulary import getVocabularyRegistry
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IActionSucceededEvent
from datetime import datetime, timedelta
from five import grok
from opengever.base.interfaces import ISequenceNumber
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
from opengever.task import util
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.source import DossierPathSourceBinder
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import form, dexterity
from plone.formwidget import autocomplete
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from plone.indexer import indexer
from plone.z3cform.traversal import FormWidgetTraversal
from z3c.relationfield.schema import RelationChoice, RelationList
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.component import getUtility
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.interface import implements, Interface
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPage
from zope.traversing.interfaces import ITraversable


class ITask(form.Schema):

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'title',
            u'issuer',
            u'task_type',
            u'responsible_client',
            u'responsible',
            u'deadline',
            u'text',
            u'relatedItems',
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
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
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

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.ogds.base.ClientsVocabulary',
        required=True)

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required = True,
        )

    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required = True,
        )

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

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
        value_type=RelationChoice(title=u"Related",
                                  source=DossierPathSourceBinder(
                navigation_tree_query=
                {'portal_type': [
                    'opengever.document.document',
                    'ftw.mail.mail'], },
                portal_type=[
                    "opengever.document.document",
                    "ftw.mail.mail"], ),
                                  ),
        required=False,
        )

    expectedStartOfWork = schema.Date(
        title =_(u"label_expectedStartOfWork", default="Start with work"),
        description = _(u"help_expectedStartOfWork", default=""),
        required = False,
        )

    expectedDuration = schema.Float(
        title = _(u"label_expectedDuration", default="Expected duration", ),
        description = _(u"help_expectedDuration", default="Duration in h"),
        required = False,
        )

    expectedCost = schema.Float(
        title = _(u"label_expectedCost", default="expected cost"),
        description = _(u"help_expectedCost", default="Cost in CHF"),
        required = False,
        )

    effectiveDuration = schema.Float(
        title = _(u"label_effectiveDuration", default="effective duration"),
        description = _(u"help_effectiveDuration", default="Duration in h"),
        required = False,
        )

    effectiveCost = schema.Float(
        title=_(u"label_effectiveCost", default="effective cost"),
        description=_(u"help_effectiveCost", default="Cost in CHF"),
        required = False,
        )

    form.omitted('predecessor')
    predecessor = schema.TextLine(
        title=_(u'label_predecessor', default=u'Predecessor'),
        description=_(u'help_predecessor', default=u''),
        required=False)

    # TODO: doesn't work with Plone 4
    #form.order_before(**{'ITransition.transition': "responsible"})

# # XXX doesn't work yet.
#@form.default_value(field=ITask['issuer'])

def default_issuer(data):
    portal_state = getMultiAdapter(
        (data.context, data.request),
        name=u"plone_portal_state")
    member = portal_state.member()
    return member.getId()


class Task(Container):
    implements(ITask)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    # REMOVED UNCOMMENT unused title function
    # def Title(self):
    #     registry = queryUtility(IRegistry)
    #     proxy = registry.forInterface(ITaskSettings)
    #     title = "#%s %s"% (
    #   getUtility(ISequenceNumber).get_number(self),self.task_type)
    #     relatedItems = getattr(self,'relatedItems',[])
    #     if len(relatedItems) == 1:
    #         title += " (%s)" % self.relatedItems[0].to_object.title
    #     elif len(relatedItems) > 1:
    #         title += " (%i Dokumente)" % len(self.relatedItems)
    #     if self.text:
    #         crop_length = int(getattr(proxy,'crop_length',20))
    #         text = self.text.encode('utf8')
    #         text = self.restrictedTraverse('@@plone').cropText(
    #   text,crop_length)
    #         text = text.decode('utf8')
    #         title += ": %s" % text
    #     return title
    @property
    def sequence_number(self):
        return self._sequence_number

    @property
    def task_type_category(self):
        for category in ['unidirectional_by_reference',
                         'unidirectional_by_value',
                         'bidirectional_by_reference',
                         'bidirectional_by_value']:
            voc = getVocabularyRegistry().get(
                self, 'opengever.task.' + category)
            if self.task_type in voc:
                return category
        return None

    @property
    def client_id(self):
        return get_client_id()


@form.default_value(field=ITask['deadline'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return datetime.today() + timedelta(5)


@form.default_value(field=ITask['responsible_client'])
def responsible_client_default_value(data):
    return get_client_id()


class ITaskView(Interface):
    pass


class View(dexterity.DisplayForm):
    implements(ITaskView)
    grok.context(ITask)
    grok.require('zope2.View')

    def getSubTasks(self):
        tasks = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': 'opengever.task.task'})
        return tasks

    def getContainingTask(self):
        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == self.context.portal_type:
            return [parent, ]
        return None

    def getSubDocuments(self):
        brains = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': 'opengever.document.document'})

        docs = []
        for doc in brains:
            docs.append(doc.getObject())

        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
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

    def getPredecessorTask(self):
        controller = ISuccessorTaskController(self.context)
        return controller.get_predecessor()

    def getSuccessorTasks(self):
        controller = ISuccessorTaskController(self.context)
        return controller.get_successors()

    def render_indexed_task(self, item):
        return indexed_task_link(item, display_client=True)



# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.

#class AddForm(dexterity.AddForm):

class AddForm(dexterity.AddForm):
    grok.name('opengever.task.task')

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            utool = getToolByName(self.context, 'portal_url')
            portal_path = utool.getPortalPath()
            # paths have to be relative to the portal
            paths = [path[len(portal_path):] for path in paths]
            self.request.set('form.widgets.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
        super(AddForm, self).update()


class TaskWidgetTraversal(FormWidgetTraversal):
    implements(ITraversable)

    def __init__(self, context, request = None):
        self.request = request

        if not ITask.providedBy(context):
            context = aq_parent(aq_inner(context))
        fti = getUtility(IDexterityFTI, name='opengever.task.task')
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


class TaskAutoCompleteSearch(grok.CodeView,
                             autocomplete.widget.AutocompleteSearch):
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
        if view_name in ['edit', 'add', '@@edit'] or \
                view_name.startswith('++add++'):
            # edit task itself
            return super_method(self)
        # add response to the task
        # XXX
        if 1:
            return
        view_name = '++add++opengever.task.task'
        view_instance = content.restrictedTraverse(view_name)
        getSecurityManager().validate(content,
                                      content,
                                      view_name,
                                      view_instance,
                                      )

    def render(self):
        pass


@indexer(ITask)
def related_items(obj):
    # FIXME this indexer seems to return ALL relatedItems and
    # does not use the `obj`..
    catalog = getUtility(ICatalog)
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
    """Indexes the client of the responsible. Since the he may be assigned
    to multiple clients, we need to use the client which was selected in the
    task.
    """

    if not obj.responsible or not obj.responsible_client:
        return ''
    else:
        return obj.responsible_client
grok.global_adapter(assigned_client, name='assigned_client')


@indexer(ITask)
def client_id(obj):
    return get_client_id()
grok.global_adapter(client_id, name='client_id')


@indexer(ITask)
def sequence_number(obj):
    """ Indexer for the sequence_number """
    return obj._sequence_number
grok.global_adapter(sequence_number, name='sequence_number')


@indexer(ITask)
def SearchableText(obj):
    """searchableText indexer."""
    context = aq_inner(obj)
    fields = [
        schema.getFields(ITask).get('title'),
        ]
    searchable = []
    for field in fields:
        try:
            data = field.get(context)
        except AttributeError:
            data = field.get(field.interface(context))
        if not data:
            continue
        if isinstance(data, unicode):
            data = data.encode('utf8')
        if isinstance(data, tuple) or isinstance(data, list):
            data = " ".join([str(a) for a in data])
        if data:
            searchable.append(data)
    # append some other attributes to the searchableText index
    # sequence_number
    seqNumb = getUtility(ISequenceNumber)
    searchable.append(str(seqNumb.get_number(obj)))

    #responsible
    info = getUtility(IContactInformation)
    task = ITask(obj)
    userid = obj.portal_membership.getMemberById(task.responsible).getId()
    searchable.append(info.describe(userid))

    return ' '.join(searchable).encode('utf-8')

grok.global_adapter(SearchableText, name='SearchableText')


@grok.subscribe(ITask, IActionSucceededEvent)
def set_dates(task, event):
    if event.action == 'task-transition-open-in-progress':
        task.expectedStartOfWork = datetime.now()
    elif event.action == 'task-transition-in-progress-resolved':
        task.date_of_completion = datetime.now()
