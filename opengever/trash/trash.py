from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.event import notify
from plone.indexer import indexer
from five import grok
from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized
from Products.CMFCore.utils import _checkPermission

class ITrashable(Interface):
    pass
    
class ITrashableMarker(Interface):
    pass

class ITrashed(Interface):
    """
    All Objects wich provide that interfaces are "moved to trash" (special delete functionality)
    """
    pass
    
#Events

class ITrashedEvent(IObjectEvent):
    pass
    
class IUntrashedEvent(IObjectEvent):
    pass
    
class TrashedEvent(ObjectEvent):
    grok.implements(ITrashedEvent)

class UntrashedEvent(ObjectEvent):
    grok.implements(IUntrashedEvent)

class Trasher(object):
    def __init__(self, context):
        self.context = context

    def trash(self):
        folder = aq_parent(aq_inner(self.context))
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()
        alsoProvides(self.context, ITrashed)
        self.context.reindexObject()
        notify(TrashedEvent(self.context))
    
    def untrash(self):
        #XXX check Permission
        folder = aq_parent(aq_inner(self.context))
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()
        noLongerProvides(self.context, ITrashed)
        self.context.reindexObject()
        notify(UntrashedEvent(self.context))
        
@indexer(Interface)
def trashIndexer(obj): 
    return ITrashed.providedBy(obj)
grok.global_adapter(trashIndexer, name="trashed")

class TrashView(grok.CodeView):
    grok.context(ITrashableMarker)
    grok.require('opengever.trash.TrashContent')
    grok.name('trashed')
    
    def __call__(self):
        paths = self.request.get('paths')
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)
                trasher = ITrashable(obj)
                trasher.trash()
        self.request.RESPONSE.redirect('%s#trash' % self.context.absolute_url())
    
    def render(self):
        super(TrashView).render()
        
class UntrashView(grok.CodeView):
    grok.context(ITrashableMarker)
    grok.require('opengever.trash.UntrashContent')
    grok.name('untrashed')
    
    def __call__(self):
        paths = self.request.get('paths')
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)
                trasher = ITrashable(obj)
                trasher.untrash()
        self.request.RESPONSE.redirect('%s#documents' % (self.context.absolute_url()))

    def render(self):
        super(UntrashView).render()