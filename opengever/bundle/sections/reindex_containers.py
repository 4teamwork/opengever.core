from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from plone import api
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import transaction


log = logging.getLogger('opengever.bundle.reindex_containers')
log.setLevel(logging.INFO)


class ReindexContainersSection(object):
    """Reindex specific indexes for containers into which objects
    were added during bundle import.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier
        self.site = api.portal.get()
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.indexes = ['modified']
        self.catalog = api.portal.get_tool('portal_catalog')

    def __iter__(self):
        for item in self.previous:
            yield item

        n_containers = len(self.bundle.containers_to_reindex)
        log.info("Reindexing {} containers after bundle import...".format(n_containers))

        for container_path in self.bundle.containers_to_reindex:
            obj = traverse(self.site, container_path, None)
            obj.reindexObject(idxs=self.indexes)

        log.info("Committing...")

        transaction.commit()

        log.info("Done reindexing {} containers".format(n_containers))
