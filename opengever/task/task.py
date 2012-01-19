from Acquisition import aq_parent, aq_inner
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import sortable_title
from collective import dexteritytextindexer
from datetime import datetime, timedelta
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.table import helper
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource, ITableSourceConfig
from opengever.base.browser.helper import client_title_helper
from opengever.base.browser.helper import css_class_from_brain
from opengever.base.interfaces import ISequenceNumber
from opengever.base.source import DossierPathSourceBinder
from opengever.globalindex.utils import indexed_task_link
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview import _ as TMF
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import external_edit_link
from opengever.tabbedview.helper import linked
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import readable_ogds_user
from opengever.task import _
from opengever.task import util
from opengever.task.helper import path_checkbox
from opengever.task.interfaces import ISuccessorTaskController
from operator import attrgetter
from plone.dexterity.content import Container
from plone.directives import form, dexterity
from plone.directives.dexterity import DisplayForm
from plone.indexer import indexer
from plone.indexer.interfaces import IIndexer
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice, RelationList
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.interface import implements, Interface
from zope.schema.vocabulary import getVocabularyRegistry


_marker = object()


class ITask(form.Schema):

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
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
        label=_(u'fieldset_additional', u'Additional'),
        fields=[
            u'expectedStartOfWork',
            u'expectedDuration',
            u'expectedCost',
            u'effectiveDuration',
            u'effectiveCost',
            u'date_of_completion',
            ],
        )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
        )

    form.widget(issuer=AutocompleteFieldWidget)
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
        required=True,
        )

    form.widget(task_type='z3c.form.browser.radio.RadioFieldWidget')
    task_type = schema.Choice(
        title=_(u'label_task_type', default=u'Task Type'),
        description=_('help_task_type', default=u''),
        required=True,
        readonly=False,
        default=None,
        missing_value=None,
        source=util.getTaskTypeVocabulary,
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
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required=True,
        )

    form.widget(deadline=DatePickerFieldWidget)
    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required=True,
        )

    form.widget(deadline=DatePickerFieldWidget)
    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required=False,
        )

    dexteritytextindexer.searchable('text')
    form.primary('text')
    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required=False,
        )

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.document.document.IDocumentSchema',
                         'opengever.task.task.ITask',
                         'ftw.mail.mail.IMail', ],
                    }),
            ),
        required=False,
        )

    form.widget(deadline=DatePickerFieldWidget)
    expectedStartOfWork = schema.Date(
        title=_(u"label_expectedStartOfWork", default="Start with work"),
        description=_(u"help_expectedStartOfWork", default=""),
        required=False,
        )

    expectedDuration = schema.Float(
        title=_(u"label_expectedDuration", default="Expected duration", ),
        description=_(u"help_expectedDuration", default="Duration in h"),
        required=False,
        )

    expectedCost = schema.Float(
        title=_(u"label_expectedCost", default="expected cost"),
        description=_(u"help_expectedCost", default="Cost in CHF"),
        required=False,
        )

    effectiveDuration = schema.Float(
        title=_(u"label_effectiveDuration", default="effective duration"),
        description=_(u"help_effectiveDuration", default="Duration in h"),
        required=False,
        )

    effectiveCost = schema.Float(
        title=_(u"label_effectiveCost", default="effective cost"),
        description=_(u"help_effectiveCost", default="Cost in CHF"),
        required=False,
        )

    form.omitted('predecessor')
    predecessor = schema.TextLine(
        title=_(u'label_predecessor', default=u'Predecessor'),
        description=_(u'help_predecessor', default=u''),
        required=False)

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


class Overview(DisplayForm, OpengeverTab):
    grok.context(ITask)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def css_class_from_brain(self, item):
        """used for display icons in the view"""
        return css_class_from_brain(item)

    def getSubTasks(self):
        tasks = self.context.getFolderContents(
            full_objects=True,
            contentFilter={'portal_type': 'opengever.task.task'})
        return tasks

    def getContainingTask(self):
        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == self.context.portal_type:
            return [parent, ]
        return None

    def responsible_link(self):
        """Render the responsible of the current task as link.
        """
        info = getUtility(IContactInformation)
        task = ITask(self.context)

        if not len(self.groups[0].widgets['responsible_client'].value):
            # in some special cases the responsible client may not be set.
            return info.render_link(task.responsible)

        if len(info.get_clients()) <= 1:
            # We have a single client setup, so we don't need to display
            # the client here.
            return info.render_link(task.responsible)

        client = client_title_helper(
            task, self.groups[0].widgets['responsible_client'].value[0])

        return client + ' / ' + info.render_link(task.responsible)

    def subtask_responsible(self, subtask):
        """Render the responsible of a subtask (object) as text.
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

    def issuer_link(self):
        info = getUtility(IContactInformation)
        task = ITask(self.context)

        if task.predecessor:
            client_id = task.predecessor.split(':')[0]
        else:
            client_id = get_client_id()

        client = client_title_helper(task, client_id)

        return client + ' / ' + info.render_link(task.issuer)

    def getPredecessorTask(self):
        controller = ISuccessorTaskController(self.context)
        return controller.get_predecessor()

    def getSuccessorTasks(self):
        controller = ISuccessorTaskController(self.context)
        return controller.get_successors()

    def render_indexed_task(self, item):
        return indexed_task_link(item, display_client=True)


class IRelatedDocumentsTableSourceConfig(ITableSourceConfig):
    """Related documents table source config
    """
    pass


def sortable_title_transform(item, value):
    """This transform should only be used for sorting items by title
    using the sortable_title indexer. Its used as wrapper for for the
    CatalogTool sortable_title indexer for making it callable like a
    normal ftw.table transform.

    This transform only works when using objects as item, using brain
    or dicts is not supported.
    """
    return sortable_title(item)()


class RelatedDocumentsTableSource(grok.MultiAdapter, BaseTableSource):
    """Related documents table source adapter
    """

    grok.implements(ITableSource)
    grok.adapts(IRelatedDocumentsTableSourceConfig, Interface)

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """
        # initalize config
        self.config.update_config()
        # get the base query from the config
        query = self.config.get_base_query()
        portal_catalog = getToolByName(self.config.context, 'portal_catalog')
        brains = portal_catalog(query)
        objects = []
        for brain in brains:
            objects.append(brain.getObject())
        for item in self.config.context.relatedItems:

            obj = item.to_object
            if (obj.portal_type == 'opengever.document.document'\
                    or obj.portal_type == 'ftw.mail.mail'):
                objects.append(obj)
        objects = self.extend_query_with_ordering(objects)
        if self.config.filter_text:
            objects = self.extend_query_with_textfilter(
                objects, self.config.filter_text)
        objects = self.extend_query_with_batching(objects)
        return objects

    def extend_query_with_ordering(self, query):
        sort_index = self.request.get('sort', '')
        column = {}
        objects = []

        if not sort_index:
            # currently we are not sorting
            return query

        if sort_index in ('draggable', 'checkbox'):
            # these columns are not sortable
            return query

        # get column that's being sorted on
        for item in self.config.columns:
            if sort_index in (item.get('column', _marker),
                              item.get('sort_index', _marker)):
                column = item
                break

        # when a transform exists for this column, we use it, since we
        # want to sort what the user is seeing.
        transform = column.get('transform', None)

        # use the sortable_title indexer function as transform for
        # sorting Title column
        if sort_index == 'sortable_title':
            transform = sortable_title_transform

        if transform:
            # when using a transform we just sort the items using the
            # transformed items
            for item in query:
                # try to safely get the value - but it may not be needed
                # for certain transforms...
                value = getattr(item, sort_index, None)
                if not value and column.get('column', None):
                    value = getattr(item, column.get('column'), None)

                objects.append((transform(item, value), item))

            # Now that we've got the sortable values for all items, sort the
            # list and then discard the values, leaving just the objects
            objects.sort()
            objects = [obj for val, obj in objects]

            if self.config.sort_reverse:
                objects.reverse()

            return objects

        else:
            # directly sort the value
            objects_sort = sorted(query, key=attrgetter(sort_index))
            if self.config.sort_reverse:
                objects_sort.reverse()
            return objects_sort

    def extend_query_with_texfilter(self, query, text):
        return query

    def extend_query_with_batching(self, query):
        """Extends the given `query` with batching filters and returns the
        new query. This method is only called when batching is enabled in
        the source config with the `batching_enabled` attribute.
        """
        return query

    def search_results(self, query):
        return query

def readable_checked_out_user(obj, user):
    """ Return the readable user who checked out the obj
    """
    catalog = obj.portal_catalog
    user = getMultiAdapter((obj, catalog), IIndexer, name='checked_out')()
    return readable_ogds_user(obj, user)

class RelatedDocuments(Documents):

    grok.name('tabbedview_view-relateddocuments')
    grok.context(ITask)
    grok.implements(IRelatedDocumentsTableSourceConfig)

    lazy = False
    columns = (
        {'column': '',
         'column_title': '',
         'transform': helper.draggable},
        {'column': '',
         'column_title': '',
         'transform': path_checkbox},

        {'column': 'title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},

        {'column': 'document_author',
         'column_title': _('label_document_author', default="Document Author"),
         'transform': readable_ogds_author},

        {'column': 'document_date',
         'column_title': _('label_document_date', default="Document Date"),
         'transform': helper.readable_date},

        {'column': 'receipt_date',
         'column_title': _('label_receipt_date', default="Receipt Date"),
         'transform': helper.readable_date},

        {'column': 'delivery_date',
         'column_title': _('label_delivery_date', default="Delivery Date"),
         'transform': helper.readable_date},

        {'column': 'checked_out',
         'column_title': TMF('label_checked_out', default="Checked out by"),
         'transform': readable_checked_out_user},
        ('', external_edit_link),
        )

    enabled_actions = [
        'send_as_email',
        'checkout',
        'checkin',
        'cancel',
        'create_task',
        'trashed',
        'send_documents',
        'copy_documents_to_remote_client',
        'move_items',
        'copy_items',
        ]

    def get_base_query(self):
        return {
            'path': {'query': '/'.join(self.context.getPhysicalPath()),
                     'depth': 2},
            'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
            }

# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.


class AddForm(dexterity.AddForm):
    grok.name('opengever.task.task')

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
        super(AddForm, self).update()

    def updateWidgets(self):
        dexterity.AddForm.updateWidgets(self)

        # omit the responsible_client field if there is only one client
        # configured.
        info = getUtility(IContactInformation)
        if len(info.get_clients()) <= 1:
            self.groups[0].fields['responsible_client'].mode = HIDDEN_MODE


class EditForm(dexterity.EditForm):
    """Standard EditForm, just require the Edit Task permission"""
    grok.context(ITask)
    grok.require('opengever.task.EditTask')

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()

        # omit the responsible_client field if there is only one client
        # configured.
        info = getUtility(IContactInformation)
        if len(info.get_clients()) <= 1:
            self.groups[0].fields['responsible_client'].mode = HIDDEN_MODE


@indexer(ITask)
def related_items(obj):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)

    # object might not have an intid yet
    try:
        obj_intid = intids.getId(aq_inner(obj))
    except KeyError:
        return []

    results = []
    relations = catalog.findRelations({'from_id': obj_intid,
                                       'from_attribute': 'relatedItems'})
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


class SearchableTextExtender(grok.Adapter):
    """ Task specific SearchableText Extender"""

    grok.context(ITask)
    grok.name('ITask')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index

        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        #responsible
        info = getUtility(IContactInformation)
        dossier = ITask(self.context)
        searchable.append(info.describe(dossier.responsible).encode(
                'utf-8'))

        return ' '.join(searchable)


@grok.subscribe(ITask, IActionSucceededEvent)
def set_dates(task, event):

    resolved_transitions = ['task-transition-in-progress-resolved',
                            'task-transition-open-resolved',
                            'task-transition-open-tested-and-closed',
                            'task-transition-in-progress-tested-and-closed',
                            ]

    if event.action == 'task-transition-open-in-progress':
        task.expectedStartOfWork = datetime.now()
    elif event.action in resolved_transitions:
        task.date_of_completion = datetime.now()
    if event.action == 'task-transition-resolved-open':
        task.date_of_completion = None


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class DocumentRedirector(grok.View):
    """Redirector View specific for documents created on a task
    redirect directly to the relateddocuments tab
    instead of the default documents tab
    """

    grok.name('document-redirector')
    grok.context(ITask)
    grok.require('zope2.View')

    def render(self):
        referer = self.context.REQUEST.environ.get('HTTP_REFERER')
        if referer.endswith('++add++opengever.document.document'):
            return self.context.REQUEST.RESPONSE.redirect(
                '%s#relateddocuments' % self.context.absolute_url())
        else:
            return self.context.REQUEST.RESPONSE.redirect(
                self.context.absolute_url())
