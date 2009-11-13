from five import grok
from zope import schema

from Acquisition import aq_inner, aq_parent
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF

from plone.dexterity.content import Item

from plone.directives import form, dexterity
from plone.app.vocabularies.workflow import WorkflowTransitionsVocabulary
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from zope.app.container.interfaces import IObjectAddedEvent
from opengever.translations.browser.edit import TranslatedEditForm

from ftw.task import util
from ftw.task import _

class IResponse(form.Schema):
    text =  schema.Text(
        title = _('label_response', default="Response"),
        description=_('help_response', default=""),
        required = True,
    )

    responsible = schema.Choice(
        title=_(u"label_responsible_Response", default="Responsible"),
        description =_(u"help_responsible_response", default=""),
        source= util.getManagersVocab,
        required = False,
    )

    deadline = schema.Datetime(
        title=_(u"label_deadline_Response", default=u"Deadline"),
        description=_(u"help_deadline_response"),
        required = False, 
    )
    
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        vocabulary=u"plone.app.vocabularies.WorkflowTransitions",
        required = True,
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
    
class View(grok.View):
    grok.context(IResponse)
    grok.require('zope2.View')
    
    def __call__(self):
        parent = aq_parent(aq_inner(self.context))
        self.request.RESPONSE.redirect(parent.absolute_url())
    
    
class ResponseEditForm(TranslatedEditForm):
    def updateWidgets(self):
        super(ResponseEditForm, self).updateWidgets()
        names = 'deadline', 'transition', 'responsible'
        for name in names:
            if name in  self.widgets.keys():
                self.widgets[name].mode = HIDDEN_MODE
                
ResponseEditView = layout.wrap_form(ResponseEditForm)
    