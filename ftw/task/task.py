from five import grok
from zope import schema

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from plone.dexterity.content import Item
from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from ftw.task import _
    
@grok.provider(IContextSourceBinder)
def possibleResponsibles(context):
    acl_users = getToolByName(context, 'acl_users')
    group = acl_users.getGroupById('Administrators')
    terms = []
    if group is not None:
        for member_id in group.getMemberIds():
            user = acl_users.getUserById(member_id)
            if user is not None:
                member_name = user.getProperty('fullname') or member_id
                terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

    return SimpleVocabulary(terms)
    

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
        source = possibleResponsibles,
        required = True,
    )
    
    expectedStartOfWork = schema.Datetime(
        title =_(u"expectedStartOfWork", default="Start with work"),
        required = True,
    )
    
    expectedDuration = schema.Float(
        title = _(u'expectedDuration',default="Expected duration"),
        required = True,
    )

    expectedCost = schema.Int(
        title = _(u"expectedCost", default="expected cost"),
        description = u'',
        required = True,
    )
    
    effectiveDuration = schema.Float(
        title = _(u"effectiveDuration", default="effective duration"),
        required = True,
    )
    
    effectiveCost = schema.Int(
        title=_(u"effectiveCost", default="effective cost")
    )

class Task(Item):
    pass
    