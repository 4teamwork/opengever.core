from five import grok
from zope.app.container.interfaces import IObjectAddedEvent
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName

from plone.versioningbehavior import MessageFactory as _
from ftw.task.behaviors import ITransitionMarker

@grok.subscribe(ITransitionMarker, IObjectAddedEvent)
def do_transition(context, event):
    """ event handler for do a transition while crating a ftw.task object
    """
    annotations = IAnnotations(context.REQUEST)
    value = annotations.get('ftw.task.task')
    if value:
        wftool = getToolByName(context, 'portal_workflow')
        wftool.doActionFor(context, value )
