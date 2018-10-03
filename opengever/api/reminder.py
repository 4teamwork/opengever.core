from opengever.task.reminder import TASK_REMINDER_OPTIONS
from opengever.task.reminder.reminder import TaskReminder
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest


error_msgs = {
    'missing_option_type': "The request body requires the 'option_type' attribute.",
    'non_existing_option_type': "The provided 'option_type' does not exists. "
                                "Use one of the following options: {}".format(
                                    ', '.join(TASK_REMINDER_OPTIONS.keys())),
}


class TaskReminderPost(Service):
    """API endpoint to set a task-reminder for the current user.

    POST /task/@reminder

    Payload: {
        "option_type": option_type
         (see opengever.task.reminder.TASK_REMINDER_OPTIONS for possible option_types)
    }

    """
    def reply(self):
        data = json_body(self.request)
        option_type = data.get('option_type')

        if not option_type:
            raise BadRequest(error_msgs.get('missing_option_type'))

        reminder_option = TASK_REMINDER_OPTIONS.get(option_type)

        if not reminder_option:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        task_reminder = TaskReminder()

        if task_reminder.get_reminder(self.context):
            self.request.response.setStatus(409)
            return super(TaskReminderPost, self).reply()

        task_reminder.set_reminder(self.context, reminder_option)

        self.request.response.setStatus(204)
        return super(TaskReminderPost, self).reply()


class TaskReminderPatch(Service):
    """API endpoint to reset a task-reminder for the current user.

    PATCH /task/@reminder

    Payload: {
        "option_type": option_type
         (see opengever.task.reminder.TASK_REMINDER_OPTIONS for possible option_types)
    }

    """
    def reply(self):
        data = json_body(self.request)
        option_type = data.get('option_type')

        reminder_option = TASK_REMINDER_OPTIONS.get(option_type)

        if option_type and not reminder_option:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        if reminder_option:
            task_reminder = TaskReminder()

            if not task_reminder.get_reminder(self.context):
                self.request.response.setStatus(404)
                return super(TaskReminderPatch, self).reply()

            task_reminder.set_reminder(self.context, reminder_option)

        self.request.response.setStatus(204)
        return super(TaskReminderPatch, self).reply()


class TaskReminderDelete(Service):
    """API endpoint to remove a task-reminder for the current user.

    DELETE /task/@reminder
    """

    def reply(self):
        task_reminder = TaskReminder()

        if not task_reminder.get_reminder(self.context):
            self.request.response.setStatus(404)
            return super(TaskReminderDelete, self).reply()

        task_reminder.clear_reminder(self.context)
        self.request.response.setStatus(204)
        return super(TaskReminderDelete, self).reply()
