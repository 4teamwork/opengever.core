from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from plone import api
from plone.app.transmogrifier.reindexobject import ReindexObjectSection
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.interface import classProvides, implements
import logging


try:
    from Products.CMFCore.CMFCatalogAware import CatalogAware  # Plone 4
except ImportError:
    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware as CatalogAware  # noqa


logger = logging.getLogger('opengever.setup.reindexobject')

SKIP_SOLR_KEY = 'skip_solr'


class GeverReindexObjectSection(ReindexObjectSection):
    classProvides(ISectionBlueprint)
    implements(ISection)

    _solr_enabled = None

    def __init__(self, transmogrifier, name, options, previous):
        super(GeverReindexObjectSection, self).__init__(
            transmogrifier, name, options, previous)

        self.skip_solr = IAnnotations(transmogrifier).get(
            SKIP_SOLR_KEY, True)

    @property
    def solr_enabled(self):
        """Boolean from registry to indicate whether Solr is enabled (memoized).
        """
        if self._solr_enabled is None:
            self._solr_enabled = api.portal.get_registry_record(
                'opengever.base.interfaces.ISearchSettings.use_solr',
                default=False)
        return self._solr_enabled

    def __iter__(self):

        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey:  # not enough info
                yield item
                continue
            path = item[pathkey]

            ob = traverse(self.context, str(path).lstrip('/'), None)
            if ob is None:
                yield item
                continue  # object not found

            if not isinstance(ob, CatalogAware):
                yield item
                continue  # can't notify portal_catalog

            if self.verbose:  # add a log to display reindexation progess
                self.counter += 1
                logger.info('Reindex object %s (%s)', path, self.counter)

            # update catalog
            if self.indexes:
                self.portal_catalog.reindexObject(ob, idxs=self.indexes)
            else:
                self.portal_catalog.reindexObject(ob)

            # solr reindexing
            if not self.skip_solr and self.solr_enabled:
                # Register collective.indexing hook, to make sure solr changes
                # are realy send to solr. See
                # collective.indexing.queue.IndexQueue.hook.
                getQueue().hook()

                # Using catalogs reindexObject does not trigger corresponding solr
                # reindexing, so we do it manually.
                processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
                processor.index(ob)

            yield item
