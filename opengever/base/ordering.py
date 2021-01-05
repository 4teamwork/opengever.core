from plone.folder.default import DefaultOrdering
from Products.CMFPlone.events import ReorderedEvent
from zope.event import notify


class GeverDefaultOrdering(DefaultOrdering):

    def moveObjectsByDelta(self, *args, **kwargs):
        """In addition to the default implementation it also triggers the
        ReorderedEvent which is necessary to properly update the getObjPositionInParent
        index.
        """
        counter = super(GeverDefaultOrdering, self).moveObjectsByDelta(*args, **kwargs)
        notify(ReorderedEvent(self.context))
        return counter
