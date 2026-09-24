from opengever.base.security import elevated_privileges
from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import register_task_type
from opengever.document.behaviors import IBaseDocument
from opengever.repository.interfaces import IRepositoryFolder
from plone import api
import logging


logger = logging.getLogger('opengever.bgtasks')

TASK_TYPE = u'update-reference-prefixes'


def reindex_children_with_new_prefix(obj):
    """Reindex `obj` and everything contained in it after its reference
    number prefix has changed.
    """
    catalog = api.portal.get_tool('portal_catalog')
    children = catalog.unrestrictedSearchResults(
        path='/'.join(obj.getPhysicalPath()))
    with elevated_privileges():
        for child in children:
            child_obj = child.getObject()
            idxs = ['reference', 'sortable_reference']
            if IBaseDocument.providedBy(child_obj):
                idxs.append('metadata')
            else:
                idxs.append('SearchableText')

            if IRepositoryFolder.providedBy(child_obj):
                idxs += ['Title',
                         'sortable_title',
                         'title_de',
                         'title_fr',
                         'title_en']

            child_obj.reindexObject(idxs=idxs)


class UpdateReferencePrefixesTask(BaseBackgroundTask):

    task_type = TASK_TYPE

    def execute(self, task, commit_checkpoint):
        args = self.get_arguments(task)
        uid = args.get(u'uid')

        if not uid:
            logger.warning(
                u'No uid in task arguments, skipping update_reference_prefixes')
            return

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog.unrestrictedSearchResults(UID=uid)
        if not results:
            logger.warning(
                u'Object %s not found in catalog, skipping '
                u'update_reference_prefixes' % uid)
            return

        try:
            obj = results[0]._unrestrictedGetObject()
        except Exception:
            logger.warning(
                u'Could not retrieve object %s, skipping '
                u'update_reference_prefixes' % uid)
            return

        if obj is None:
            logger.warning(
                u'getObject() returned None for %s, skipping '
                u'update_reference_prefixes' % uid)
            return

        reindex_children_with_new_prefix(obj)


register_task_type(TASK_TYPE, UpdateReferencePrefixesTask)
