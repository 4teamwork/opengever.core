"""
Migrate private folders and their contents for renamed users.
"""

from opengever.usermigration.base import BaseUserMigration
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')


def objpath(obj):
    return '/'.join(obj.getPhysicalPath())


class PrivateFoldersMigrator(BaseUserMigration):

    def migrate(self):
        mtool = api.portal.get_tool('portal_membership')
        private_root = mtool.getMembersFolder()

        private_folder_moves = []

        for old_userid, new_userid in self.principal_mapping.items():
            new_private_folder = private_root.get(new_userid)
            old_private_folder = private_root.get(old_userid)

            if not old_private_folder:
                # Nothing to do
                continue

            if not new_private_folder:
                # New private folder doesn't exist yet, let's create it
                mtool.createMemberArea(member_id=new_userid)
                new_private_folder = private_root[new_userid]

            # Move all content from the old private folder into the new one,
            # and delete the old private folder
            for obj in old_private_folder.objectValues():
                api.content.move(obj, new_private_folder)
                logger.info(
                    "Merged object %s into new private "
                    "folder" % objpath(obj))

            # Old private folder should now be empty - remove it
            assert old_private_folder.objectIds() == []
            api.content.delete(old_private_folder)
            logger.info(
                "Removing empty private folder"
                " %r" % objpath(old_private_folder))
            private_folder_moves.append(
                (objpath(old_private_folder),
                    old_userid, new_private_folder.id))

        results = {
            'private_folders': {
                'moved': private_folder_moves,
                'copied': [],
                'deleted': []},
        }
        return results
