from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_path_filter
from opengever.base.security import elevated_privileges
from opengever.base.solr import batched_solr_results
from opengever.base.solr import OGSolrDocument
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import register_task_type
from opengever.dossier.indexers import TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX
from opengever.globalindex.handlers.task import sync_task
from plone import api
from zope.component import queryUtility
import logging


logger = logging.getLogger('opengever.bgtasks')

TASK_TYPE = u'reindex-dossier-title'


def reindex_containing_subdossier_for_contained_objects(dossier):
    """When a subdossier's title changes, update the ``containing_subdossier``
    index of all contained objects (documents, mails and tasks) so they don't
    show an outdated title in the ``subdossier`` column.
    """
    containing_subdossier_title = dossier.Title()

    solr = queryUtility(ISolrSearch)
    filters = make_path_filter('/'.join(dossier.getPhysicalPath()), depth=-1)
    filters += [
        u'portal_type:({})'.format(
            u' OR '.join(TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX)),
    ]

    with elevated_privileges():
        for batch in batched_solr_results(filters=filters, fl='UID,portal_type,path'):
            for doc in batch:
                solr.manager.connection.add({
                    "UID": doc['UID'],
                    "containing_subdossier": {"set": containing_subdossier_title},
                })


def reindex_containing_dossier_for_contained_objects(dossier):
    """When a dossier's title changes, update the ``containing_dossier``
    index of all contained objects.
    """
    containing_dossier_title = dossier.Title()

    solr = queryUtility(ISolrSearch)
    filters = make_path_filter('/'.join(dossier.getPhysicalPath()), depth=-1)

    with elevated_privileges():
        for batch in batched_solr_results(filters=filters, fl='UID,portal_type,path'):
            for doc in batch:
                solr.manager.connection.add({
                    "UID": doc['UID'],
                    "containing_dossier": {"set": containing_dossier_title},
                })
                if doc['portal_type'] == 'opengever.task.task':
                    obj = OGSolrDocument(doc).getObject()
                    sync_task(obj, None)


def reindex_dossier_title(dossier):
    """Dispatch to the containing_dossier or containing_subdossier reindex,
    depending on whether `dossier` is a subdossier.
    """
    if dossier.is_subdossier():
        reindex_containing_subdossier_for_contained_objects(dossier)
    else:
        reindex_containing_dossier_for_contained_objects(dossier)


class ReindexDossierTitleTask(BaseBackgroundTask):

    task_type = TASK_TYPE

    def execute(self, task, commit_checkpoint):
        args = self.get_arguments(task)
        uid = args.get(u'uid')

        if not uid:
            logger.warning(
                u'No uid in task arguments, skipping reindex_dossier_title')
            return

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog.unrestrictedSearchResults(UID=uid)
        if not results:
            logger.warning(
                u'Object %s not found in catalog, skipping '
                u'reindex_dossier_title' % uid)
            return

        try:
            obj = results[0]._unrestrictedGetObject()
        except Exception:
            logger.warning(
                u'Could not retrieve object %s, skipping '
                u'reindex_dossier_title' % uid)
            return

        if obj is None:
            logger.warning(
                u'getObject() returned None for %s, skipping '
                u'reindex_dossier_title' % uid)
            return

        reindex_dossier_title(obj)


register_task_type(TASK_TYPE, ReindexDossierTitleTask)
