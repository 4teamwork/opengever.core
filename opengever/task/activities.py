from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity import base_notification_center
from opengever.activity import SYSTEM_ACTOR_ID
from opengever.activity.base import BaseActivity
from opengever.activity.model.notification import Notification
from opengever.activity.roles import TASK_OLD_RESPONSIBLE_ROLE
from opengever.base.model import get_locale
from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.task.response_description import ResponseDescription
from plone import api
from Products.CMFPlone import PloneMessageFactory


class TaskAddedActivity(BaseActivity):
    """Activity representation for adding a task.
    """

    def __init__(self, context, request, parent):
        super(TaskAddedActivity, self).__init__(context, request)
        self.parent = parent

    @property
    def kind(self):
        return PloneMessageFactory(u'task-added', default=u'Task added')

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('transition_label_default', u'Task opened'))

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('label_task_added', u'New task opened by ${user}',
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
             self.context.text if self.context.text else u'-'],
            [_('label_responsible', u'Responsible'),
             self.context.get_responsible_actor().get_label()],
            [_('label_issuer', u'Issuer'),
             self.context.get_issuer_actor().get_label()]
        ]

    def before_recording(self):
        self.center.add_task_responsible(self.context,
                                         self.context.responsible)
        self.center.add_task_issuer(self.context, self.context.issuer)


class BaseTaskResponseActivity(BaseActivity):
    """Abstract base class for all task-response related activities.

    The TaskResponseActivity class is a representation for every activity which
    can be done on a task. It provides every needed attribute/methods to
    record the activity in the notification center based on a response object.
    """

    def __init__(self, context, request, response):
        super(BaseTaskResponseActivity, self).__init__(context, request)
        self.response = response

    @property
    def summary(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).msg())

    @property
    def label(self):
        return self.translate_to_all_languages(
            ResponseDescription.get(response=self.response).label())

    @property
    def description(self):
        return {get_locale(): self.response.text}


class TaskCommentedActivity(BaseTaskResponseActivity):
    """Activity representation for commenting a task.
    """
    @property
    def kind(self):
        return PloneMessageFactory(u'task-commented', default=u'Task commented')


class TaskTransitionActivity(BaseTaskResponseActivity):
    """Activity which represents a transition task transition change.
    """

    IGNORED_TRANSITIONS = [
        'transition-add-subtask',
        'task-transition-reassign',
        'forwarding-transition-reassign',
        'forwarding-transition-reassign-refused',
    ]

    @property
    def kind(self):
        return self.response.transition

    def record(self):
        if self._is_ignored_transition():
            return

        return super(TaskTransitionActivity, self).record()

    def _is_ignored_transition(self):
        return self.response.transition in self.IGNORED_TRANSITIONS


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


class TaskReminderActivity(BaseActivity):
    kind = 'task-reminder'

    def __init__(self, sql_context, request):
        super(TaskReminderActivity, self).__init__(sql_context, request)

        # A TaskReminderAcitivty requires a SQL-Object as a context because we
        # have no plone-object on activity-generation due to multi-admin setup.
        #
        # Thus we need to change the notification-center instance to the
        # default instead the PloneNotifiactionCenter
        self.center = base_notification_center()

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('task_reminder_activity_summary', u'Deadline is on ${deadline}',
              mapping={'deadline': self._deadline()}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        return {}

    def _deadline(self):
        return api.portal.get_localized_time(
            self.context.deadline, long_format=True)

    def record(self, notify_for_user_id):
        """Adds the activity and the related notification for the given user-id.

        Let the notification-center handle creating the activity and
        notifications will not work. The notification-center would create
        notifications for all watchers of a given resource. But we only want
        to create one notification for the current acitvity-object and the given
        user-id.
        """
        activity = self.add_activity()
        Notification(userid=notify_for_user_id, activity=activity)
        map(lambda dispatcher: dispatcher.dispatch_notifications(activity),
            self.center.dispatchers)

    def add_activity(self):
        # Because we use the default NotificationCenter, we need to provide
        # the oguid instead the object itself. See __init__ for more information.
        return self.center._add_activity(
            self.context.oguid,
            self.kind,
            self.title,
            self.label,
            self.summary,
            SYSTEM_ACTOR_ID,
            self.description)
