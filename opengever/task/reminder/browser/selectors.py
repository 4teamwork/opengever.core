from opengever.task import _
from opengever.task.reminder import TASK_REMINDER_OPTIONS
from opengever.task.reminder.reminder import TaskReminder
from Products.Five.browser import BrowserView
from zope.i18n import translate
import json


class TaskReminderSelector(BrowserView):

    def current_reminder_title(self):
        for option in self.reminder_options():
            if option.get('selected'):
                return option.get('option_title')

    def reminder_options(self):
        options = []
        reminder_option = TaskReminder().get_reminder(self.context)

        options.append({
            'option_type': 'no-reminder',
            'option_title': translate(_('no_reminder', default='No reminder'),
                                      context=self.request),
            'sort_order': -1,
            'selected': reminder_option is None,
            })

        for option in TASK_REMINDER_OPTIONS.values():
            selected = option.option_type == reminder_option.option_type if \
                reminder_option else None
            options.append({
                'option_type': option.option_type,
                'sort_order': option.sort_order,
                'option_title': translate(
                    option.option_title, context=self.request),
                'selected': selected,
            })

        return options

    def init_state(self):
        return json.dumps({
            'endpoint': self.context.absolute_url() + '/@reminder',
            'reminder_options': self.reminder_options(),
            'error_msg': translate(_('error_while_updating_task_reminder',
                                     default="There was an error while "
                                             "updating the reminder"),
                                   context=self.request)
        })
