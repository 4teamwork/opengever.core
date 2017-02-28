from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.monkey.patches.cmf_catalog_aware import DeactivatedCatalogIndexing  # noqa
from zope.interface import classProvides
from zope.interface import implements


class DisabledCatalogIndexing(object):
    """Disable automatic indexing of objects during the pipeline.

    Indexing will be performed for all objects once at the end of the
    pipeline.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        with DeactivatedCatalogIndexing():
            for item in self.previous:
                yield item
