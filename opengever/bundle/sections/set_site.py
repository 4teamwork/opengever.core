from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.component.hooks import setSite
from zope.interface import classProvides
from zope.interface import implements


class SetSiteSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.every = int(options.get('every', 100))
        self.previous = previous

    def __iter__(self):
        count = 0
        for item in self.previous:
            if count and count % self.every == 0:
                # Periodically set the Plone site in order to reduce
                # memory usage (high-water-mark). This, in combination with
                # regular cPickleCache garbage collection, seems to get rid of
                # leaking references that then can be collected by the Python
                # garbage collector.
                setSite(self.transmogrifier.context)
            count += 1
            yield item
