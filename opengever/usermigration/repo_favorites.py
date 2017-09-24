"""
Migrate repository favorites.
"""

from opengever.portlets.tree.favorites import ANNOTATION_KEY
from persistent.list import PersistentList
from plone import api
from zope.annotation import IAnnotations
import logging


logger = logging.getLogger('opengever.usermigration')


class RepoFavoritesMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "RepoFavoritesMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

    def migrate(self):
        favorites_moves = []

        catalog = api.portal.get_tool('portal_catalog')
        reporoots = [b.getObject() for b in catalog.unrestrictedSearchResults(
            portal_type='opengever.repository.repositoryroot')]

        for root in reporoots:
            root_path = '/'.join(root.getPhysicalPath())
            annotations = IAnnotations(root).get(ANNOTATION_KEY)
            if not annotations:
                continue

            for old_userid, new_userid in self.principal_mapping.items():
                if old_userid in annotations:
                    # Create target favorites list if it doesn't exist yet
                    if new_userid not in annotations:
                        annotations[new_userid] = PersistentList()

                    # Copy over each entry to new list if not present yet
                    for uuid in annotations[old_userid]:
                        if uuid not in annotations[new_userid]:
                            annotations[new_userid].append(uuid)

                    # Drop favorites for old user ID
                    annotations.pop(old_userid)

                    favorites_moves.append((root_path, old_userid, new_userid))
                    logger.info("Migrated repo favorites for %s (%s -> %s)" % (
                        root_path, old_userid, new_userid))

        results = {
            'favorites': {
                'moved': favorites_moves,
                'copied': [],
                'deleted': []},
        }
        return results
