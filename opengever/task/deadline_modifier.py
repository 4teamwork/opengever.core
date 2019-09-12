from opengever.task.browser.transitioncontroller import get_checker
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.reminder.reminder import TaskReminder
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
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

    def is_modify_allowed(self, include_agency=True):
        """Check if the current user is allowed to modify the deadline:
        - state is `in-progress` or `open`
        - and is issuer or agency member (adminstrator or issuing
        orgunit agency member).
        """
        # TODO: should be solved by a own permission 'modify_deadline'
        # but right now the issuer has not a sperate role.

        if not self.context.is_editable:
            return False

        checker = get_checker(self.context)
        if not include_agency:
            return checker.current_user.is_issuer or checker.current_user.is_responsible
        else:
            return (checker.current_user.is_issuer
                    or checker.current_user.current_user.is_responsible
                    or checker.current_user.in_issuing_orgunits_inbox_group
                    or checker.current_user.is_administrator)

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
        TaskReminder().recalculate_remind_day_for_obj(self.context)

    def sync_deadline(self, new_deadline, text, transition):
        sync_task_response(self.context, self.context.REQUEST, 'deadline',
                           transition, text, new_deadline=new_deadline)
