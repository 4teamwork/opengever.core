from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.interface import classProvides, implements
import gc
import transaction


class SavepointSection(object):
    """Custom Savepoint section that also triggers garbage collection of the
    ZODB cPickleCache after creating a savepoint, in order to limit memory
    usage growth.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.every = int(options.get('every', 1000))
        self.previous = previous

    def __iter__(self):
        count = 0
        for item in self.previous:
            count = (count + 1) % self.every
            if count == 0:
                transaction.savepoint(optimistic=True)

                # Trigger garbage collection for the cPickleCache
                self.transmogrifier.context._p_jar.cacheGC()

                # Also trigger Python garbage collection.
                # This doesn't seem to affect the memory high-water-mark,
                # but results in a more stable / predictable growth over time.
                #
                # But should this cause problems at some point, it's safe
                # to remove this without affecting the max memory consumed.
                gc.collect()

            yield item
