from opengever.task.interfaces import IDeadlineModifier
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from zExceptions import Unauthorized
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent


@implementer(IDeadlineModifier)
@adapter(ITask)
class DeadlineModifier(object):

    def __init__(self, context):
        self.context = context

    def is_modify_allowed(self):
        """Check if the current user is allowed to modify the deadline:
        - state is `in-progress`, `open`, `planned` or `resolved`
        - user has modify portal content permission.
        """
        return self.context.is_editable and api.user.has_permission(
            'Modify portal content', obj=self.context)

    def modify_deadline(self, new_deadline, text, transition):
        """Handles the whole deadline mofication process:
        - Set the new deadline
        - Add response
        - Handle synchronisation if needed
        """

        if not self.is_modify_allowed():
            raise Unauthorized

        self.update_deadline(new_deadline, text, transition)
        self.sync_deadline(new_deadline, text, transition)

    def update_deadline(self, new_deadline, text, transition):
        add_simple_response(
            self.context, text=text,
            field_changes=(
                (ITask['deadline'], new_deadline),
            ),
            transition=transition,
            supress_events=True)

        self.context.deadline = new_deadline
        notify(ObjectModifiedEvent(self.context))
        self.context.update_reminder_trigger_dates()

    def sync_deadline(self, new_deadline, text, transition):
        sync_task_response(self.context, self.context.REQUEST, 'deadline',
                           transition, text, new_deadline=new_deadline)
