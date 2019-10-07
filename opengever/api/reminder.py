from opengever.task.reminder import Reminder
from opengever.task.reminder import REMINDER_TYPE_REGISTRY
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import alsoProvides
from zope.schema import ValidationError


error_msgs = {
    'missing_option_type': "The request body requires the 'option_type' attribute.",
    'non_existing_option_type': "The provided 'option_type' does not exists. "
                                "Use one of the following options: {}".format(
                                    ', '.join(REMINDER_TYPE_REGISTRY.keys())),
}


class TaskReminderGet(Service):
    """API endpoint to get a task-reminder for the current user.

    GET /task/@reminder
    """

    def reply(self):
        reminder = self.context.get_reminder()
        if not reminder:
            raise NotFound

        reminder_data = reminder.serialize(json_compat=True)
        reminder_data['@id'] = '/'.join((self.context.absolute_url(), '@reminder'))
        return reminder_data


class TaskReminderPost(Service):
    """API endpoint to set a task-reminder for the current user.

    POST /task/@reminder

    Payload: {
        "option_type": option_type,
        "params": dict of parameters
    }

    (see opengever.task.reminder.REMINDER_TYPE_REGISTRY for possible option_types,
    and the specific reminder subclass for supported/required parameters)
    """

    def reply(self):
        data = json_body(self.request)
        option_type = data.get('option_type')
        params = data.get('params')

        if not option_type:
            raise BadRequest(error_msgs.get('missing_option_type'))

        if option_type not in REMINDER_TYPE_REGISTRY:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        reminder_data = {'option_type': option_type, 'params': params}

        try:
            reminder = Reminder.deserialize(reminder_data)
        except (ValidationError, ValueError) as exc:
            raise BadRequest(repr(exc))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if self.context.get_reminder():
            self.request.response.setStatus(409)
            return super(TaskReminderPost, self).reply()

        self.context.set_reminder(reminder)
        self.context.sync()

        self.request.response.setStatus(204)
        return super(TaskReminderPost, self).reply()


class TaskReminderPatch(Service):
    """API endpoint to reset a task-reminder for the current user.

    PATCH /task/@reminder

    Payload: {
        "option_type": option_type,
        "params": dict of parameters
    }
    (see opengever.task.reminder.REMINDER_TYPE_REGISTRY for possible option_types,
    and the specific reminder subclass for supported/required parameters)
    """

    def reply(self):
        data = json_body(self.request)

        option_type = data.get('option_type')
        params = data.get('params')

        if option_type and option_type not in REMINDER_TYPE_REGISTRY:
            raise BadRequest(error_msgs.get('non_existing_option_type'))

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        if option_type or params:
            existing_reminder = self.context.get_reminder()
            if not existing_reminder:
                self.request.response.setStatus(404)
                return super(TaskReminderPatch, self).reply()

            # Pick existing settings if not given (PATCH semantics)
            option_type = option_type or existing_reminder.option_type
            params = params if 'params' in data else existing_reminder.params

            reminder_data = {'option_type': option_type, 'params': params}
            try:
                reminder = Reminder.deserialize(reminder_data)
            except (ValidationError, ValueError) as exc:
                raise BadRequest(repr(exc))

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
