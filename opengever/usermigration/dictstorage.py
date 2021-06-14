"""
Helpers for migrating user and group related data in dictstorage SQL tables.
"""

from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.usermigration.base import BaseUserMigration
import logging


logger = logging.getLogger('opengever.usermigration')


def rreplace(s, old, new, maxreplace=-1):
    """Pendant to str.replace() that replaces substrings from the right
    instead of the left (if maxreplace != -1).
    """
    return new.join(s.rsplit(old, maxreplace))


class DictstorageMigrator(BaseUserMigration):
    """Migrates occurences of a username in dictstorage keys in SQL.

    Will replace the first occurence of the old user ID *from the right*
    if the key ends with '-olduserid'.

    This approach will fail if there exists a user ID that is a substring of
    another user ID with a dash, for example:
    'user42' and 'other-user42'. That should be highly unlikely though.
    """

    def __init__(self, portal, principal_mapping, mode='move'):
        super(DictstorageMigrator, self).__init__(
            portal, principal_mapping, mode=mode
        )
        self.session = create_session()

    def _migrate_dictstorage_keys(self):
        moved = []

        entries = self.session.query(DictStorageModel).all()
        for entry in entries:
            old_key = entry.key
            for old_userid in self.principal_mapping:
                if old_key.endswith('-{}'.format(old_userid)):
                    new_userid = self.principal_mapping[old_userid]
                    self._verify_user(new_userid)
                    # Replace one occurence of old_userid from the right
                    new_key = rreplace(old_key, old_userid, new_userid, 1)
                    entry.key = new_key
                    moved.append((old_key, old_userid, new_userid))
                    logger.info(new_key)
        return moved

    def migrate(self):
        keys_moved = self._migrate_dictstorage_keys()

        results = {
            'keys': {
                'moved': keys_moved, 'copied': [], 'deleted': []},
        }
        return results
