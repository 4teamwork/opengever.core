from opengever.bgtasks.task import BaseBackgroundTask
from opengever.bgtasks.task import register_task_type
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
import logging


logger = logging.getLogger('opengever.bgtasks')

TASK_TYPE = u'reindex-object-security'


class ReindexObjectSecurityTask(BaseBackgroundTask):

    task_type = TASK_TYPE

    def execute(self, task, commit_checkpoint):
        import opengever.bgtasks.patches as _patches_mod

        args = self.get_arguments(task)
        uid = args.get(u'uid')
        skip_self = args.get(u'skip_self', False)

        if not uid:
            logger.warning(u'No uid in task arguments, skipping reindexObjectSecurity')
            return

        site = getSite()
        if site is None:
            logger.warning(
                u'No site available, skipping reindexObjectSecurity for %s' % uid)
            return

        catalog = getToolByName(site, 'portal_catalog', None)
        if catalog is None:
            logger.warning(
                u'portal_catalog not found, skipping reindexObjectSecurity for %s' % uid)
            return

        results = catalog.unrestrictedSearchResults(UID=uid)
        if not results:
            logger.warning(
                u'Object %s not found in catalog, skipping reindexObjectSecurity' % uid)
            return

        try:
            obj = results[0]._unrestrictedGetObject()
        except Exception:
            logger.warning(
                u'Could not retrieve object %s, skipping reindexObjectSecurity' % uid)
            return

        if obj is None:
            logger.warning(
                u'getObject() returned None for %s, skipping reindexObjectSecurity' % uid)
            return

        _patches_mod._original_reindex_object_security(obj, skip_self=skip_self)


register_task_type(TASK_TYPE, ReindexObjectSecurityTask)
