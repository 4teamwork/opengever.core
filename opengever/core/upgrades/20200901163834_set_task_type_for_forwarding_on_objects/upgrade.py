from ftw.upgrade import UpgradeStep
from opengever.inbox.forwarding import IForwarding


FORWARDING_TASK_TYPE_ID = u'forwarding_task_type'


class SetTaskTypeForForwardingOnObjects(UpgradeStep):
    """Set task_type for forwarding on objects.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IForwarding.__identifier__}
        for obj in self.objects(query, 'Set task_type on forwarding objects'):
            # attributestorage, bypass field fallback to default
            task_type = obj.__dict__.get('task_type', None)
            if not task_type:
                obj.task_type = FORWARDING_TASK_TYPE_ID
