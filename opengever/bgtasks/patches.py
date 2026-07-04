from opengever.base.model import create_session
from opengever.base.monkey.patching import MonkeyPatch
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.reindex_object_security import TASK_TYPE
from opengever.bgtasks.task import queue_task
from plone import api
import json
import logging


logger = logging.getLogger('opengever.bgtasks')

_original_reindex_object_security = None


class PatchCMFCatalogAwareReindexObjectSecurity(MonkeyPatch):
    """Patch CMFCatalogAware.reindexObjectSecurity to enqueue a background task.

    Captures whatever implementation is currently on the method at patch time
    (typically ftw.solr's recursive_index_security version) and stores it as
    the original for the task handler to call out-of-band.
    """

    def __call__(self):
        global _original_reindex_object_security

        # Ensure patch from ftw.solr is applied first
        import ftw.solr.patches  # noqa,
        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        _original_reindex_object_security = CMFCatalogAware.reindexObjectSecurity

        from opengever.base.monkey.patches.cmf_catalog_aware import IDisableCatalogIndexing
        from opengever.ogds.base.utils import get_current_admin_unit
        from zope.globalrequest import getRequest

        def reindexObjectSecurity(self, skip_self=False):

            if IDisableCatalogIndexing.providedBy(getRequest()):
                return

            uid = self.UID()
            if not uid:
                return _original_reindex_object_security(self, skip_self=skip_self)

            catalog = api.portal.get_tool('portal_catalog')
            results = catalog.unrestrictedSearchResults(UID=uid)
            if not results:
                return _original_reindex_object_security(self, skip_self=skip_self)

            admin_unit = get_current_admin_unit()
            if admin_unit is None:
                return _original_reindex_object_security(self, skip_self=skip_self)

            admin_unit_id = admin_unit.unit_id

            session = create_session()
            existing = (session.query(BackgroundTask)
                        .filter_by(task_type=TASK_TYPE,
                                   admin_unit_id=admin_unit_id,
                                   status=TASK_STATUS_PENDING)
                        .all())
            for existing_task in existing:
                args = json.loads(existing_task.task_arguments or u'{}')
                if args.get(u'uid') == uid:
                    session.delete(existing_task)

            queue_task(TASK_TYPE, admin_unit_id,
                       arguments={u'uid': uid, u'skip_self': skip_self})

        locals()['__patch_refs__'] = False
        self.patch_refs(CMFCatalogAware, 'reindexObjectSecurity', reindexObjectSecurity)
