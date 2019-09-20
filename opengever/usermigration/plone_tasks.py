"""
Migrate user IDs in Plone tasks (issuers, responsibles, responses)
"""

from opengever.base.response import IResponseContainer
from opengever.ogds.base.utils import ogds_service
from opengever.task.task import ITask
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')

FIELDS_TO_CHECK = ('responsible', 'issuer')


class PloneTasksMigrator(object):
    """This migrator changes the `issuer` and `responsible` fields on
    Plone tasks, as well as updating responses on tasks as needed.

    It does not however fix local roles assigned to Plone tasks - these can
    be fixed using the "local roles" migration in ftw.usermigration.
    """

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "PloneTasksMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

        # Keep track of tasks that need reindexing
        self.to_reindex = set()

        self.task_moves = {
            'responsible': [],
            'issuer': [],
        }
        self.response_moves = {
            'creator': [],
            'responsible_before': [],
            'responsible_after': [],
        }

    def _verify_user(self, userid):
        ogds_user = ogds_service().fetch_user(userid)
        if ogds_user is None:
            msg = "User '{}' not found in OGDS!".format(userid)
            raise UserMigrationException(msg)

    def _fix_responses(self, obj):
        container = IResponseContainer(obj)
        path = '/'.join(obj.getPhysicalPath())
        for response in container:
            response_identifier = '%s - Response #%s' % (path, response.response_id)

            # Fix response creator
            creator = getattr(response, 'creator', '')
            if creator in self.principal_mapping:
                logger.info("Fixing 'creator' for %s" % response_identifier)
                new_userid = self.principal_mapping[creator]
                response.creator = new_userid
                self.response_moves['creator'].append((
                    response_identifier, creator, new_userid))

            for change in response.changes:
                # Fix responsible [before|after]
                if change.get('field_id') == 'responsible':
                    before = change.get('before', '')
                    if before in self.principal_mapping:
                        new_userid = self.principal_mapping[before]
                        change['before'] = unicode(new_userid)
                        # Need to flag changes to track mutations - see #3419
                        response.changes._p_changed = True
                        logger.info(
                            "Fixed 'responsible:before' for change in %s "
                            "(%s -> %s)" % (
                                response_identifier, before, new_userid))
                        self.response_moves['responsible_before'].append((
                            response_identifier, before, new_userid))

                    after = change.get('after', '')
                    if after in self.principal_mapping:
                        new_userid = self.principal_mapping[after]
                        change['after'] = unicode(new_userid)
                        # Need to flag changes to track mutations - see #3419
                        response.changes._p_changed = True
                        logger.info(
                            "Fixed 'responsible:after' for change in %s "
                            "(%s -> %s)" % (
                                response_identifier, after, new_userid))
                        self.response_moves['responsible_after'].append((
                            response_identifier, after, new_userid))

    def _migrate_plone_task(self, obj):
        task = ITask(obj)

        for field_name in FIELDS_TO_CHECK:
            # Check 'responsible' and 'issuer' fields
            old_userid = getattr(task, field_name, None)

            if old_userid in self.principal_mapping:
                path = '/'.join(obj.getPhysicalPath())
                logger.info('Fixing %r for %s' % (field_name, path))
                new_userid = self.principal_mapping[old_userid]
                setattr(task, field_name, new_userid)
                self.to_reindex.add(obj)
                self.task_moves[field_name].append(
                    (path, old_userid, new_userid))

    def migrate(self):
        catalog = api.portal.get_tool('portal_catalog')

        # Verify all new users exist before doing anything
        for old_userid, new_userid in self.principal_mapping.items():
            self._verify_user(new_userid)

        all_tasks = [b.getObject() for b in catalog.unrestrictedSearchResults(
            object_provides=ITask.__identifier__)]

        for obj in all_tasks:
            self._migrate_plone_task(obj)
            self._fix_responses(obj)

        for obj in self.to_reindex:
            # Reindex 'responsible' and 'issuer' for changed objects.
            logger.info('Reindexing %s' % '/'.join(obj.getPhysicalPath()))
            obj.reindexObject(idxs=FIELDS_TO_CHECK)

        results = {
            'task_issuers': {
                'moved': self.task_moves['issuer'],
                'copied': [],
                'deleted': []},
            'task_responsibles': {
                'moved': self.task_moves['responsible'],
                'copied': [],
                'deleted': []},
            'response_creators': {
                'moved': self.response_moves['creator'],
                'copied': [],
                'deleted': []},
            'response_responsible_before': {
                'moved': self.response_moves['responsible_before'],
                'copied': [],
                'deleted': []},
            'response_responsible_after': {
                'moved': self.response_moves['responsible_after'],
                'copied': [],
                'deleted': []},
        }
        return results
