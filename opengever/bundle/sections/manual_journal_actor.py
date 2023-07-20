from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.journal import ManualJournalActor
from zope.interface import classProvides
from zope.interface import implements


class ManualJournalActorSection(object):
    """Add request flag to create journal entries with the items creator
    if given in the bundle.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for item in self.previous:
            if item.get('_creator'):
                with ManualJournalActor(item.get('_creator')):
                    yield item
            else:
                yield item
