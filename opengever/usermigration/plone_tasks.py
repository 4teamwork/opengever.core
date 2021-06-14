"""
Migrate user IDs in Plone tasks (issuers, responsibles, responses, reminders)
"""

from opengever.base.response import IResponseContainer
from opengever.task.reminder.storage import REMINDER_ANNOTATIONS_KEY
from opengever.task.task import ITask
from opengever.usermigration.base import BasePloneObjectAttributesMigrator
from zope.annotation import IAnnotations
import logging


logger = logging.getLogger('opengever.usermigration')


class PloneTasksMigrator(BasePloneObjectAttributesMigrator):
    """This migrator changes the `issuer` and `responsible` fields on
    Plone tasks, as well as updating responses on tasks as needed.
    It also migrates task reminders.

    It does not however fix local roles assigned to Plone tasks - these can
    be fixed using the "local roles" migration in ftw.usermigration.
    """

    fields_to_migrate = ('responsible', 'issuer')
    interface_to_query = ITask
    interface_to_adapt = ITask

    def __init__(self, portal, principal_mapping, mode='move'):
        super(PloneTasksMigrator, self).__init__(
            portal, principal_mapping, mode=mode
        )

        self.response_moves = {
            'creator': [],
            'responsible_before': [],
            'responsible_after': [],
        }

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

    def _migrate_task_reminders(self, obj):
        annotations = IAnnotations(obj)
        if REMINDER_ANNOTATIONS_KEY not in annotations:
            return

        reminders = annotations[REMINDER_ANNOTATIONS_KEY]
        for old_userid in list(reminders.keys()):
            if old_userid in self.principal_mapping:
                new_userid = self.principal_mapping[old_userid]
                reminders[new_userid] = reminders[old_userid]
                del reminders[old_userid]

    def _migrate_object(self, obj):
        super(PloneTasksMigrator, self)._migrate_object(obj)
        self._migrate_task_reminders(obj)
        self._fix_responses(obj)

    def _report_results(self):
        results = super(PloneTasksMigrator, self)._report_results()
        results.update({
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
        })
        return results
