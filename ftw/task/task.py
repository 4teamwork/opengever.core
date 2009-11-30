from five import grok
from zope import schema
from zope.interface import implements, Interface
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPage
from zope.component import queryMultiAdapter, getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.container.interfaces import IObjectAddedEvent

from Acquisition import aq_parent, aq_inner
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from datetime import datetime, timedelta
from z3c.relationfield.relation import TemporaryRelationValue

from plone.formwidget import autocomplete
from plone.formwidget.autocomplete import AutocompleteFieldWidget

from plone.z3cform.traversal import WidgetTraversal
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.content import Item, Container

from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.app.dexterity.behaviors.related import IRelatedItems
from plone.namedfile.field import NamedImage

from ftw.task import util
from ftw.task import _

from opengever.translations.browser import edit, add

class ITask(form.Schema):
    
    form.fieldset(
        u'additional',
        label = _(u'fieldset_additional', u'Additional'),
        fields = [
            u'expectedStartOfWork',
            u'expectedDuration',
            u'expectedCost',
            u'effectiveDuration',
            u'effectiveCost',
            ]
        )
    
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u"Title"),
        required = True,    
    )
    form.primary('text')
    text = RichText(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required = True,
    )

    deadline = schema.Date(
        title=_(u"label_deadline", default=u""),
        description=_(u"help_deadline", default=u"Deadline"),
        required = True,
    )
    
    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default="select an responsible Manger"),
        source = util.getManagersVocab,
        required = False,
    )
    
    expectedStartOfWork = schema.Date(
        title =_(u"label_expectedStartOfWork", default="Start with work"),
        description = _(u"help_expectedStartOfWork", default=""),
        required = False,
    )
    
    expectedDuration = schema.Float(
        title = _(u"label_expectedDuration",default="Expected duration"),
        description = _(u"help_expectedDuration", default=""),
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
        required = False
    )

@grok.subscribe(ITask, IObjectAddedEvent)
def setID(task, event):
    task._sequence_number = util.create_sequence_number( task )
    
class Task(Container):
    implements(ITask)
    
    @property
    def sequence_number(self):
        return self._sequence_number

@form.default_value(field=ITask['deadline'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return datetime.today() + timedelta(5)

@form.default_value(field=IRelatedItems['relatedItems'])
def pathsDefaultValue(data):
#XXX Don't work yet
    paths = data.request.get('paths', None)
    from zope.component import getUtility
    from zope.app.intid.interfaces import IIntIds
    intids = getUtility( IIntIds )
    if paths:
        pathlist = []
        for item in paths:
            obj = data.context.restrictedTraverse( item.encode())
            id = intids.getId(obj)
            pathlist.append(TemporaryRelationValue(id))
        return pathlist
    return []
                
class ITaskView(Interface):
    pass
#class View(grok.View):
class View(dexterity.DisplayForm):
    implements(ITaskView)
    grok.context(ITask)
    grok.require('zope2.View')
    
    def getSubTasks(self):
        tasks = self.context.getFolderContents(full_objects=False, contentFilter={'portal_type':'ftw.task.task'})
        return tasks
    
    def getResponses(self):
        responses = self.context.getFolderContents(full_objects=True, contentFilter={'portal_type':'ftw.task.response'})
        return responses

class TaskWidgetTraversal(WidgetTraversal):
    implements(ITraversable)

    def __init__(self, context,request = None):
        self.request = request
        
        if not ITask.providedBy(context):
            context = aq_parent( aq_inner( context ) )
        fti = getUtility(IDexterityFTI, name='ftw.task.task')
        adder = queryMultiAdapter((context, self.request, fti),
                              IBrowserPage)

        self.context = adder    
        
grok.global_adapter(TaskWidgetTraversal, ((ITask, IBrowserRequest)), ITraversable, name=u"widget")
grok.global_adapter(TaskWidgetTraversal, ((ITaskView, IBrowserRequest)), ITraversable, name=u"widget")


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
        getSecurityManager().validate(content, content, view_name, view_instance)
        
    def render(self):
        pass
    
    