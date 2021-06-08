from opengever.ogds.models.service import ogds_service
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.usermigration.exceptions import UserMigrationException
from plone import api
import logging


logger = logging.getLogger('opengever.usermigration')

FIELDS_TO_CHECK = ('responsible', 'issuer')


class TaskTemplateMigrator(object):
    """Migrate the `issuer` and `responsible` fields on task templates."""

    def __init__(self, portal, principal_mapping, mode='move', strict=True):
        self.portal = portal
        self.principal_mapping = principal_mapping

        if mode != 'move':
            raise NotImplementedError(
                "TaskTemplateMigrator only supports 'move' mode")
        self.mode = mode
        self.strict = strict

        # Keep track of tasktemplates that need reindexing
        self.to_reindex = set()

        self.task_moves = {
            'responsible': [],
            'issuer': [],
        }

    def _verify_user(self, userid):
        ogds_user = ogds_service().fetch_user(userid)
        if ogds_user is None:
            msg = "User '{}' not found in OGDS!".format(userid)
            raise UserMigrationException(msg)

    def _migrate_plone_task(self, obj):
        task = ITaskTemplate(obj)

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
            object_provides=ITaskTemplate.__identifier__)]

        for obj in all_tasks:
            self._migrate_plone_task(obj)

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
        }
        return results
