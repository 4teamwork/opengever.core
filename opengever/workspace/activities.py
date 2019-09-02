from opengever.activity.base import BaseActivity
from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE


class ToDoAssignedActivity(BaseActivity):
    """Activity representation for assigning a todo.
    """

    kind = u'todo-assigned'

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_todo_assigned_activity', u'ToDo assigned'))

    @property
    def summary(self):
        responsible = Actor.lookup(self.context.responsible)
        user = Actor.lookup(self.actor_id)

        msg = _(u'summary_todo_assigned_activity',
                u'Assigned to ${responsible} by ${user}',
                mapping={'responsible': responsible.get_label(with_principal=False),
                         'user': user.get_label(with_principal=False)})

        return self.translate_to_all_languages(msg)

    @property
    def description(self):
        return {}

    def before_recording(self):
        self.center.remove_watchers_from_resource_by_role(
            self.context, TODO_RESPONSIBLE_ROLE)

        if self.context.responsible is not None:
            self.center.add_watcher_to_resource(
                self.context, self.context.responsible,
                TODO_RESPONSIBLE_ROLE)
