from opengever.base.touched import RECENTLY_TOUCHED_KEY
from zope.annotation import IAnnotations
import logging


logger = logging.getLogger('opengever.usermigration')


class RecentlyTouchedMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "RecentlyTouchedMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

    def migrate(self):
        annotations = IAnnotations(self.portal)
        touched_store = annotations.get(RECENTLY_TOUCHED_KEY)
        if not touched_store:
            return

        recently_touched_moves = []

        for old_userid, new_userid in self.principal_mapping.items():
            if old_userid not in touched_store:
                continue

            touched_store[new_userid] = touched_store[old_userid]
            del touched_store[old_userid]

            recently_touched_moves.append(
                ('recently_touched', old_userid, new_userid)
            )

        results = {
            'recently_touched': {
                'moved': recently_touched_moves,
                'copied': [],
                'deleted': []},
        }
        return results
