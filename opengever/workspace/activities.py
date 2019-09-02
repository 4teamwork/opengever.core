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


class ToDoModifiedBaseActivity(BaseActivity):
    """Base class for ToDo modified activity.
    """

    kind = u'todo-modified'

    @property
    def description(self):
        return {}


class ToDoClosedActivity(ToDoModifiedBaseActivity):
    """Activity representation for closing a todo.
    """

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_todo_closed_activity', u'ToDo closed'))

    @property
    def summary(self):
        user = Actor.lookup(self.actor_id)
        msg = _(u'Closed by ${user}',
                mapping={'user': user.get_label(with_principal=False)})

        return self.translate_to_all_languages(msg)


class ToDoReopenedActivity(ToDoModifiedBaseActivity):
    """Activity representation for reopening a todo.
    """

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_todo_reopened_activity', u'ToDo reopened'))

    @property
    def summary(self):
        user = Actor.lookup(self.actor_id)
        msg = _(u'Reopened by ${user}',
                mapping={'user': user.get_label(with_principal=False)})

        return self.translate_to_all_languages(msg)


class ToDoCommentedActivity(ToDoModifiedBaseActivity):

    def __init__(self, context, request, response_container, response):
        super(ToDoCommentedActivity, self).__init__(context, request)
        self.response_container = response_container
        self.response = response

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_todo_commented_activity', u'ToDo commented'))

    @property
    def summary(self):
        user = Actor.lookup(self.response.creator)
        msg = _(u'Commented by ${user}',
                mapping={'user': user.get_label(with_principal=False)})

        return self.translate_to_all_languages(msg)
