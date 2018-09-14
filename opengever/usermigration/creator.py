"""
Helper for migrating creators on Dexterity objects.
"""

from opengever.usermigration.exceptions import UserMigrationException
from plone import api
from zope.component import getMultiAdapter
import logging


logger = logging.getLogger('opengever.usermigration')


class CreatorMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "CreatorMigrator only supports 'move' mode as of yet")
        self.mode = mode

        self.strict = strict
        self.catalog = api.portal.get_tool('portal_catalog')
        self.acl_users = api.portal.get_tool('acl_users')

    def _get_objects(self):
        brains = self.catalog.unrestrictedSearchResults()
        for brain in brains:
            yield brain.getObject()

    def _verify_user(self, userid):
        pas_search = getMultiAdapter((self.portal, self.portal.REQUEST),
                                     name='pas_search')
        users = pas_search.searchUsers(id=userid)
        if len(users) < 1:
            msg = "User '{}' not found in acl_users!".format(userid)
            if self.strict:
                raise UserMigrationException(msg)
            else:
                logger.warn(msg)

    def _migrate_creators(self, obj):
        if not hasattr(obj, 'creators'):
            return [], []

        changed = False
        moved = []
        modified_idxs = set()
        path = '/'.join(obj.getPhysicalPath())

        new_creators = []
        for old_userid in obj.creators:
            if old_userid in self.principal_mapping:
                new_userid = self.principal_mapping[old_userid]
                logger.info("Migrating creator(s) for {} ({} -> {})".format(
                    path, old_userid, new_userid))
                self._verify_user(new_userid)
                new_creators.append(new_userid)
                moved.append((path, old_userid, new_userid))
                modified_idxs.update(['listCreators', 'Creator'])
                changed = True
            else:
                new_creators.append(old_userid)
        if changed:
            obj.creators = tuple(new_creators)

        return list(modified_idxs), moved

    def migrate(self):
        creators_moved = []

        objects = self._get_objects()
        for obj in objects:
            modified_idxs = []

            # Migrate creators
            idxs, moved = self._migrate_creators(obj)
            modified_idxs.extend(idxs)
            creators_moved.extend(moved)
            if modified_idxs:
                obj.reindexObject(idxs=modified_idxs)

        results = {
            'creators': {
                'moved': creators_moved, 'copied': [], 'deleted': []},
        }

        return results
