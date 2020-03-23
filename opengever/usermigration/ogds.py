"""
Helpers for migrating user and group related data in OGDS SQL tables.
"""

from opengever.ogds.models.service import ogds_service
from opengever.usermigration.exceptions import UserMigrationException
import logging


logger = logging.getLogger('opengever.usermigration')


class OGDSMigrator(object):

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "OGDSMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

    def _verify_group(self, groupid):
        ogds_group = ogds_service().fetch_group(groupid)
        if ogds_group is None:
            msg = "Group '{}' not found in OGDS!".format(groupid)
            raise UserMigrationException(msg)

    def _migrate_group(self, org_unit, column_name):
        moved = []
        old_groupid = getattr(org_unit, column_name).groupid

        if old_groupid in self.principal_mapping:
            new_groupid = self.principal_mapping[old_groupid]
            logger.info("Migrating {} for {} ({} -> {})".format(
                column_name, str(org_unit), old_groupid, new_groupid))
            self._verify_group(new_groupid)
            new_group = ogds_service().fetch_group(new_groupid)
            setattr(org_unit, column_name, new_group)
            moved.append((str(org_unit), old_groupid, new_groupid))

        return moved

    def migrate(self):
        users_groups_moved = []
        inbox_groups_moved = []

        org_units = ogds_service().all_org_units()

        for org_unit in org_units:
            # Migrate users_group
            moved = self._migrate_group(org_unit, 'users_group')
            users_groups_moved.extend(moved)

            # Migrate inbox_group
            moved = self._migrate_group(org_unit, 'inbox_group')
            inbox_groups_moved.extend(moved)

        results = {
            'users_groups': {
                'moved': users_groups_moved, 'copied': [], 'deleted': []},
            'inbox_groups': {
                'moved': inbox_groups_moved, 'copied': [], 'deleted': []},
        }
        return results
