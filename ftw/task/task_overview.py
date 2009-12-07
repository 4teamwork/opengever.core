from five import grok
from zope.interface import implements, Interface

from plone.dexterity.content import Container

from plone.directives import form, dexterity


class ITaskOverview(form.Schema):
    pass
    
class TaskOverview(Container):
    implements(ITaskOverview)
                
class ITaskOverviewView(Interface):
    pass

class MyTasks(dexterity.DisplayForm):
    implements(ITaskOverviewView)
    grok.context(ITaskOverview)
    grok.require('zope2.View')