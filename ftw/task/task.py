from five import grok
from zope import schema

from zope.component import queryMultiAdapter, getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces.browser import IBrowserPage
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from plone.dexterity.interfaces import IDexterityFTI

from plone.dexterity.content import Item, Container
from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage
from ftw.task import util

from ftw.task import _

class ITask(form.Schema):
    
    title = schema.TextLine(
        title=_(u"title", default=u"Title"),
        description=_(u"descTitle", default=u"Enter a short, descriptive title for the issue. A good title will make it easier for project managers to identify and respond to the issue."),        
        required = True,    
    )
    
    text = schema.Text(
        title=_(u"text", default=u"Text"),
        description=_(u"descText", default=u"Enter all your Angaben"),
        required = True,
    )

    deadline = schema.Datetime(
        title=_(u"deadline", default=u"Deadline"),
        required = True, 
    )
    
    priority = schema.Choice(
        title= _(u"priority", default="Priority"),
        values = (_(u"critical"), _(u"important"), _(u"medium"), _(u"low")),
        required =True,
    )
    
    responsible = schema.Choice(
        title=_(u"responsible", default="Responsible"),
        description =_(u"descResponsible", default="select an responsible Manger"),
        source = util.getManagersVocab,
        required = False,
    )
    
    expectedStartOfWork = schema.Datetime(
        title =_(u"expectedStartOfWork", default="Start with work"),
        required = False,
    )
    
    expectedDuration = schema.Float(
        title = _(u'expectedDuration',default="Expected duration"),
        required = False,
    )

    expectedCost = schema.Int(
        title = _(u"expectedCost", default="expected cost"),
        description = u'',
        required = False,
    )
    
    effectiveDuration = schema.Float(
        title = _(u"effectiveDuration", default="effective duration"),
        required = False,
    )
    
    effectiveCost = schema.Int(
        title=_(u"effectiveCost", default="effective cost"),
        required = False
    )

class Task(Container):
    pass

#class View(grok.View):
class View(dexterity.DisplayForm):
    grok.context(ITask)
    grok.require('zope2.View')
    
    def getResponseForm(self):
        import pdb; pdb.set_trace( )
        fti = getUtility(IDexterityFTI, name='ftw.task.response')
        adder = queryMultiAdapter((self.context, self.request, fti),
                              IBrowserPage)
        return adder.form_instance()
        
    def getSubTasks(self):
        tasks = self.context.getFolderContents(full_objects=True, contentFilter={'portal_type':'ftw.task.task'})
        return tasks
    
    def getResponses(self):
        responses = self.context.getFolderContents(full_objects=True, contentFilter={'portal_type':'ftw.task.response'})
        import pdb; pdb.set_trace( )
        return responses
