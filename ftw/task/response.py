from five import grok
from zope import schema

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF

from plone.dexterity.content import Item
from plone.directives import form, dexterity
from plone.app.vocabularies.workflow import WorkflowTransitionsVocabulary
from zope.app.container.interfaces import IObjectAddedEvent, IObjectModifiedEvent
from ftw.task import util

from ftw.task import _

class IResponse(form.Schema):
    text =  schema.Text(
        title = _('response', default="Response"),
        required = True,
    )

    responsible = schema.Choice(
        title=_(u"responsible", default="Responsible"),
        description =_(u"descResponsible", default="select an responsible Manger"),
        source= util.getManagersVocab,
        required = False,
    )

    deadline = schema.Datetime(
        title=_(u"deadline", default=u"Deadline"),
        required = False, 
    )
    
    transition = schema.Choice(
        title=_("transition", default="transition"),
        vocabulary=u"plone.app.vocabularies.WorkflowTransitions",
        required = False,
    )

@grok.subscribe(IResponse, IObjectAddedEvent)
def changeTask(response, event):
    task = response.__parent__
    changes = []
    if response.deadline != None and task.deadline != response.deadline:
        changes.append((_('deadline', default="deadline"), task.deadline.strftime('%d.%m.%Y') , response.deadline.strftime('%d.%m.%Y')))
        task.deadline = response.deadline
    if response.responsible != None and task.responsible != response.responsible:
        changes.append((_('responsible', default="responsible"), task.responsible, response.responsible))
        task.responsible = response.responsible
        
    response.changes = changes

class Response(Item):
    pass
"""
class View(grok.View):
    grok.context(IResponse)
    grok.require('zope2.View') """