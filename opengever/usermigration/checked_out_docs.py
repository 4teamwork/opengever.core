"""
Migrate user IDs in checked out state for documents as well as WebDAV locks.
"""

from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY  # noqa
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.models.service import ogds_service
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
from zope.component import getMultiAdapter
import logging
from plone.locking.interfaces import IRefreshableLockable


logger = logging.getLogger('opengever.usermigration')


class CheckedOutDocsMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "CheckedOutDocsMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

    def _verify_user(self, userid):
        ogds_user = ogds_service().fetch_user(userid)
        if ogds_user is None:
            msg = "User '{}' not found in OGDS!".format(userid)
            raise UserMigrationException(msg)

    def _migrate_checked_out_doc(self, doc, old_userid, new_userid):
        # Migrate "checked out by" information and reindex
        manager = getMultiAdapter((doc, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        key = CHECKIN_CHECKOUT_ANNOTATIONS_KEY
        if manager.annotations[key] == old_userid:
            manager.annotations[key] = new_userid
            logger.info('Reindexing %s' % '/'.join(doc.getPhysicalPath()))
            doc.reindexObject(idxs=['checked_out'])

        # Migrate WebDAV locks
        lockable = IRefreshableLockable(doc)
        if lockable.locked():
            locks = doc.wl_lockmapping().values()
            for lock in locks:
                if not lock.getCreator():
                    continue

                if lock._creator[1] == old_userid:
                    lock._creator = (lock._creator[0], new_userid)

    def migrate(self):
        catalog = api.portal.get_tool('portal_catalog')
        checked_out_docs_moves = []

        for old_userid, new_userid in self.principal_mapping.items():

            checked_out_docs = [
                b.getObject() for b in
                catalog.unrestrictedSearchResults(
                    portal_type='opengever.document.document',
                    checked_out=old_userid)]

            for doc in checked_out_docs:
                self._verify_user(new_userid)
                self._migrate_checked_out_doc(doc, old_userid, new_userid)
                checked_out_docs_moves.append((doc, old_userid, new_userid))

        results = {
            'checked_out_docs': {
                'moved': checked_out_docs_moves,
                'copied': [],
                'deleted': []},
        }
        return results
