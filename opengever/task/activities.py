from opengever.activity import notification_center
from opengever.activity.base import BaseActivity
from opengever.activity.model.subscription import TASK_OLD_RESPONSIBLE_ROLE
from opengever.base.model import get_locale
from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.task.response_description import ResponseDescription
from plone import api
from Products.CMFPlone import PloneMessageFactory


class TaskActivity(BaseActivity):
    """Abstract base class for all task-related activities.

    The TaskActivity class is a representation for every activity which can
    be done with or on a task. It provides every needed attribute/methods to
    record the activity in the notification center.

    """
    def __init__(self, context, request, parent):
        super(TaskActivity, self).__init__(context, request)
        self.parent = parent


class TaskCommentedActivity(TaskActivity):
    """Activity representation for commenting a task.
    """
    def __init__(self, context, request, parent, response):
        super(TaskCommentedActivity, self).__init__(context, request, parent)
        self.response = response

    @property
    def kind(self):
        return PloneMessageFactory(u'task-commented', default=u'Task commented')

    @property
    def description(self):
        return {get_locale(): self.response.text}

    @property
    def summary(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).msg())

    @property
    def label(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).label())


class TaskAddedActivity(TaskActivity):
    """Activity representation for adding a task."""

    @property
    def kind(self):
        return PloneMessageFactory(u'task-added', default=u'Task added')

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('transition_label_default', u'Task added'))

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('label_task_added', u'New task added by ${user}',
                mapping={'user': actor.get_label(with_principal=False)})
        return self.translate_to_all_languages(msg)

    @property
    def description(self):
        descriptions = {}
        for code in self._get_supported_languages():
            descriptions[code] = self.render_description_markup(
                self.collect_description_data(code), code)

        return descriptions

    def render_description_markup(self, data, language):
        msg = u'<table><tbody>'
        for label, value in data:
            msg = u'{}<tr><td class="label">{}</td><td>{}</td></tr>'.format(
                msg, self.translate(label, language), value)

        return u'{}</tbody></table>'.format(msg)

    def collect_description_data(self, language):
        """Returns a list with [label, value] pairs.
        """
        return [
            [_('label_task_title', u'Task title'), self.context.title],
            [_('label_deadline', u'Deadline'),
             api.portal.get_localized_time(str(self.context.deadline))],
            [_('label_task_type', u'Task Type'),
             self.context.get_task_type_label(language=language)],
            [_('label_dossier_title', u'Dossier title'),
             self.parent.title],
            [_('label_text', u'Text'),
             self.context.text if self.context.text else u'-' ]
        ]

    def before_recording(self):
        self.center.add_task_responsible(self.context,
                                         self.context.responsible)
        self.center.add_task_issuer(self.context, self.context.issuer)


class TaskTransitionActivity(TaskActivity):
    """Activity which represents a transition task transition change.
    """

    IGNORED_TRANSITIONS = [
        'transition-add-subtask',
        'task-transition-reassign',
        'forwarding-transition-reassign',
        'forwarding-transition-reassign-refused',
    ]

    def __init__(self, context, response):
        self.context = context
        self.request = self.context.REQUEST
        self.transition = response.transition
        self.response = response
        self.center = notification_center()

    @property
    def kind(self):
        return self.response.transition

    @property
    def summary(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).msg())

    @property
    def label(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).label())

    @property
    def actor(self):
        return api.user.get_current().getId()

    @property
    def description(self):
        return {get_locale(): self.response.text}

    def record(self):
        if self._is_ignored_transition():
            return

        return super(TaskTransitionActivity, self).record()

    def _is_ignored_transition(self):
        return self.transition in self.IGNORED_TRANSITIONS


class TaskReassignActivity(TaskTransitionActivity):
    """Updates the watcherlist for the current task because of the responsible
    change on the task.

    The issuer and the old and the new responsible should be notified.
    After recording the activity the old responsible should be removed from
    the watchers list.
    """

    def before_recording(self):
        """Adds new responsible to watchers list.
        And change roles for old responsible from TASK_RESPONSIBLE
        to OLD_RESPONSIBLE.
        """
        change = self.response.get_change('responsible')
        self.center.add_task_responsible(self.context, self.context.responsible)

        self.center.remove_task_responsible(self.context, change.get('before'))
        self.center.add_watcher_to_resource(
            self.context, change.get('before'), TASK_OLD_RESPONSIBLE_ROLE)

    def after_recording(self):
        """Remove old responsible from watchers list.
        """
        change = self.response.get_change('responsible')
        self.center.remove_watcher_from_resource(
            self.context, change.get('before'), TASK_OLD_RESPONSIBLE_ROLE)

    def _is_ignored_transition(self):
        return False
