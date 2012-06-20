from zope.interface import Interface, alsoProvides, noLongerProvides
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.event import notify
from plone.indexer import indexer
from five import grok
from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from opengever.trash import _


class ITrashable(Interface):
    pass


class ITrashableMarker(Interface):
    pass


class ITrashed(Interface):
    """
    All Objects wich provide that interfaces
    are "moved to trash" (special delete functionality)
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
        # check trash permission
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


class TrashView(grok.View):
    grok.context(ITrashableMarker)
    grok.require('opengever.trash.TrashContent')
    grok.name('trashed')

    def __call__(self):
        paths = self.request.get('paths')
        catalog = getToolByName(self.context, 'portal_catalog')
        trashed = False
        if paths:
            for item in paths:
                obj = self.context.restrictedTraverse(item)
                brains = catalog(path=item)

                # check that the object isn't already trashed
                if not brains:
                    msg = _(
                        u'could not trash the object ${obj}, '
                        'it is already trashed',
                        mapping={'obj': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue
                # check that the document isn't checked_out
                if brains[0].checked_out:
                    msg = _(
                        u'could not trash the object ${obj}, it is checked out',
                        mapping={'obj': obj.Title().decode('utf-8')})
                    IStatusMessage(self.request).addStatusMessage(
                        msg, type='error')
                    continue

                trasher = ITrashable(obj)
                trasher.trash()
                trashed = True
                msg = _(u'the object ${obj} trashed',
                    mapping={'obj': obj.Title().decode('utf-8')})
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='info')

        else:
            msg = _(u'You have not selected any items')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

        if trashed:
            return self.request.RESPONSE.redirect(
                '%s#trash' % self.context.absolute_url())
        else:
            return self.request.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

    def render(self):
        super(TrashView).render()


class UntrashView(grok.View):
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

            return self.request.RESPONSE.redirect('%s#documents' % (
                self.context.absolute_url()))

        else:
            msg = _(u'You have not selected any items')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')

            return self.request.RESPONSE.redirect(
                '%s#trash' % self.context.absolute_url())

    def render(self):
        super(UntrashView).render()
