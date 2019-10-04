from opengever.task.reminder import REMINDER_TYPE_REGISTRY
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides
from opengever.task.reminder import Reminder


error_msgs = {
    'missing_option_type': "The request body requires the 'option_type' attribute.",
    'non_existing_option_type': "The provided 'option_type' does not exists. "
                                "Use one of the following options: {}".format(
                                    ', '.join(REMINDER_TYPE_REGISTRY.keys())),
}


class TaskReminderPost(Service):
    """API endpoint to set a task-reminder for the current user.

    POST /task/@reminder

    Payload: {
        "option_type": option_type
         (see opengever.task.reminder.REMINDER_TYPE_REGISTRY for possible option_types)
    }

    """
    def reply(self):
        data = json_body(self.request)
        option_type = data.get('option_type')

        if not option_type:
            raise BadRequest(error_msgs.get('missing_option_type'))

        if option_type not in REMINDER_TYPE_REGISTRY:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if self.context.get_reminder():
            self.request.response.setStatus(409)
            return super(TaskReminderPost, self).reply()

        reminder = Reminder.create(option_type, {})
        self.context.set_reminder(reminder)
        self.context.sync()

        self.request.response.setStatus(204)
        return super(TaskReminderPost, self).reply()


class TaskReminderPatch(Service):
    """API endpoint to reset a task-reminder for the current user.

    PATCH /task/@reminder

    Payload: {
        "option_type": option_type
         (see opengever.task.reminder.REMINDER_TYPE_REGISTRY for possible option_types)
    }

    """
    def reply(self):
        data = json_body(self.request)
        option_type = data.get('option_type')

        if option_type and option_type not in REMINDER_TYPE_REGISTRY:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if option_type:

            if not self.context.get_reminder():
                self.request.response.setStatus(404)
                return super(TaskReminderPatch, self).reply()

            reminder = Reminder.create(option_type, {})
            self.context.set_reminder(reminder)
            self.context.sync()

        self.request.response.setStatus(204)
        return super(TaskReminderPatch, self).reply()


class TaskReminderDelete(Service):
    """API endpoint to remove a task-reminder for the current user.

    DELETE /task/@reminder
    """

    def reply(self):
        if not self.context.get_reminder():
            self.request.response.setStatus(404)
            return super(TaskReminderDelete, self).reply()

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        self.context.clear_reminder()
        self.context.sync()

        self.request.response.setStatus(204)
        return super(TaskReminderDelete, self).reply()
