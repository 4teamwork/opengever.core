from collections import Counter
from datetime import timedelta
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from plone import api
import logging


TOLERANCE = timedelta(seconds=5)

log = logging.getLogger('ftw.upgrade')


class TouchModifiedTimestampForObjectsWhereChangedIsNewer(UpgradeStep):
    """Touch modified timestamp for objects where changed is newer.
    """

    deferrable = True

    def __call__(self):
        log.info("Checking catalog for items that have a 'changed' "
                 "timestamp that that is newer than  'modified'...")

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(sort_on='path')
        total_items = len(brains)
        log.info('Catalog contains %s items total.' % total_items)

        found_total = 0
        found_by_type = Counter()

        with NightlyIndexer(idxs=["modified"],
                            index_in_catalog_only=True) as indexer:
            msg = "Touching 'modified' for affected objects"
            for brain in ProgressLogger(msg, brains):
                changed = brain.changed
                modified = brain.modified.asdatetime()

                if not changed:
                    continue

                if changed > (modified + TOLERANCE):
                    found_total += 1
                    found_by_type[brain.portal_type] += 1
                    obj = brain.getObject()
                    obj.setModificationDate()
                    indexer.add_by_brain(brain)

        log.info("Updated 'modified' for %s brains." % found_total)
        for portal_type, count in found_by_type.items():
            log.info('  %-40s : %s' % (portal_type, count))
        log.info('(Out of %s total objects in catalog)' % total_items)
