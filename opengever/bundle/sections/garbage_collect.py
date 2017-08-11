from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.component.hooks import setSite
from zope.interface import classProvides
from zope.interface import implements
import gc


def garbage_collect(transmogrifier):
    # In order to get rid of leaking references, the Plone site needs to be
    # re-set in regular intervals using the setSite() hook. This reassigns
    # it to the SiteInfo() module global in zope.component.hooks, and
    # therefore allows the Python garbage collector to cut loose references
    # it was previously holding on to.
    setSite(transmogrifier.context)

    # Trigger garbage collection for the cPickleCache
    transmogrifier.context._p_jar.cacheGC()

    # Also trigger Python garbage collection.
    gc.collect()

    # (These two don't seem to affect the memory high-water-mark,
    # but result in a more stable / predictable growth over time.
    #
    # But should this cause problems at some point, it's safe
    # to remove these without affecting the max memory consumed.)


class GarbageCollectSection(object):
    """Section used to facilitate regular garbage collection.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.every = int(options.get('every', 100))
        self.previous = previous

    def __iter__(self):
        count = 0
        for item in self.previous:
            count = (count + 1) % self.every
            if count == 0:
                garbage_collect(self.transmogrifier)

            yield item
