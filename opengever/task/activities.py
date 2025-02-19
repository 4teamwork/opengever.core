from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity import base_notification_center
from opengever.activity.base import BaseActivity
from opengever.activity.model.notification import Notification
from opengever.activity.roles import TASK_OLD_RESPONSIBLE_ROLE
from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.model import get_locale
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import SYSTEM_ACTOR_ID
from opengever.task import _
from opengever.task import FINISHED_TASK_STATES
from opengever.task.response_description import ResponseDescription
from plone import api
from plone.app.textfield import IRichTextValue
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.utils import safe_unicode


class BaseTaskActivity(BaseActivity):

    @property
    def dossier_title(self):
        """If the task is in a subdossier, return its title, otherwise
        return the title of the main dossier (or inbox for a forwarding)"""

        # context can be a plone task or a task model
        dossier_title = self.context.get_containing_dossier_title()
        subdossier_title = self.context.get_containing_subdossier()

        container_title = safe_unicode(subdossier_title or dossier_title)
        return container_title

    @property
    def title(self):
        task_title = super(BaseTaskActivity, self).title

        if not self.dossier_title:
            # Just to be safe, but this should not happen, except in tests
            # where tasks are created directly on the site root.
            return task_title

        return {
            code: u"{dossier_title} - {task_title}".format(
                dossier_title=self.dossier_title, task_title=task_title[code]
            )
            for code in self._get_supported_languages()
        }


class TaskAddedActivity(BaseTaskActivity):
    """Activity representation for adding a task.
    """

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

        if self.context.is_private:
            msg = _('label_private_task_added',
                    default=u'New task (private) opened by ${user}',
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
            msg = u'{}<tr><td valign="top" class="label">{}</td><td>'.format(
                msg, self.translate(label, language))
            # Break lines correctly in the table rows
            if value:
                if IRichTextValue.providedBy(value):
                    msg += value.output
                else:
                    msg += u"<br />".join(value.splitlines())
            msg += u"</td></tr>"
        return u'{}</tbody></table>'.format(msg)

    def collect_description_data(self, language):
        """Returns a list with [label, value] pairs.
        """
        informed_principals = [Actor.lookup(actorid).get_label() for actorid in
                               self.context.informed_principals]
        data = [
            [_('label_task_title', u'Task title'), self.context.title],
            [_('label_deadline', u'Deadline'),
             api.portal.get_localized_time(str(self.context.deadline))],
            [_('label_task_type', u'Task Type'),
             self.context.get_task_type_label(language=language)],
            [_('label_dossier_title', u'Dossier title'),
             self.dossier_title],
            [_('label_text', u'Text'),
             self.context.text if self.context.text else u'-'],
            [_('label_responsible', u'Responsible'),
             self.context.get_responsible_actor().get_label()],
            [_('label_issuer', u'Issuer'),
             self.context.get_issuer_actor().get_label()],
            [_('label_informed_principals', u'Info at'),
             ", ".join(informed_principals) or '-'],
        ]
        if self.context.get_is_subtask():
            parent = aq_parent(aq_inner(self.context))
            data.insert(
                4, [_('label_containing_task', u'Containing tasks'), parent.title]
            )
        return data

    def before_recording(self):
        self.center.add_task_responsible(self.context,
                                         self.context.responsible)
        self.center.add_task_issuer(self.context, self.context.issuer)
        for principal in self.context.informed_principals:
            self.center.add_watcher_to_resource(
                self.context, principal, omit_watcher_added_event=True)

    def after_recording(self):
        for principal in self.context.informed_principals:
            self.center.remove_watcher_from_resource(
                self.context, principal, WATCHER_ROLE)


class TaskWatcherAddedActivity(BaseTaskActivity):
    """Activity representation for a watcher being added to a task.
    """

    def __init__(self, context, request, watcherid):
        super(TaskWatcherAddedActivity, self).__init__(context, request)
        self.watcherid = watcherid

    @property
    def kind(self):
        return PloneMessageFactory(u'task-watcher-added', default=u'Watcher added to task')

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('summary_task_watcher_added', u'Added as watcher of the task by ${user}',
              mapping={'user': Actor.lookup(self.actor_id).get_link()}))

    @property
    def description(self):
        return {}

    @property
    def label(self):
        msg = _('label_task_watcher_added', u'Added as watcher of the task')
        return self.translate_to_all_languages(msg)

    def add_activity(self):
        return super(TaskWatcherAddedActivity, self).add_activity(
            notification_recipients=[self.watcherid])


class BaseTaskResponseActivity(BaseTaskActivity):
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
        'transition-cancel-subtask',
        'transition-close-subtask',
        'task-transition-reassign',
        'task-transition-change-issuer',
        'forwarding-transition-reassign',
        'forwarding-transition-reassign-refused',
        'forwarding-transition-change-issuer',
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


class TaskChangeIssuerActivity(TaskTransitionActivity):

    def before_recording(self):
        change = ResponseDescription.get(response=self.response).get_change('issuer')
        if not change or change.get('before') == self.context.issuer:
            return

        self.center.add_task_issuer(self.context, self.context.issuer)
        self.center.remove_task_issuer(self.context, change.get('before'))

    def _is_ignored_transition(self):
        return False


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
        change = ResponseDescription.get(response=self.response).get_change('responsible')

        # If the `responsible` is not part of the response changes, it means
        # that the same responsible in another org unit has been selected. So
        # there is no need to manipulate the watcher list, everything stays
        # the same.
        if not change or change.get('before') == self.context.responsible:
            return

        self.center.add_task_responsible(self.context, self.context.responsible)
        self.center.remove_task_responsible(self.context, change.get('before'))
        self.center.add_watcher_to_resource(
            self.context, change.get('before'), TASK_OLD_RESPONSIBLE_ROLE)

    def after_recording(self):
        """Remove old responsible from watchers list.
        """
        change = ResponseDescription.get(response=self.response).get_change('responsible')
        self.center.remove_watcher_from_resource(
            self.context, change.get('before'), TASK_OLD_RESPONSIBLE_ROLE)

    def _is_ignored_transition(self):
        return False


class TaskReminderActivity(BaseTaskActivity):
    kind = 'task-reminder'
    IGNORED_STATES = FINISHED_TASK_STATES + ['task-state-resolved']
    system_activity = True

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

        if self.context.review_state in self.IGNORED_STATES:
            return

        activity = self.add_activity()
        notification = Notification(userid=notify_for_user_id, activity=activity)

        for dispatcher in self.center.dispatchers:
            if TASK_REMINDER_WATCHER_ROLE in dispatcher.get_dispatched_roles_for(
                    notification.activity.kind, notify_for_user_id):
                dispatcher.dispatch_notification(notification)

    def add_activity(self):
        # Because we use the default NotificationCenter, we need to provide
        # the oguid instead the object itself. See __init__ for more information.
        return self.center._add_activity(
            self.context.oguid,
            self.kind,
            self.title,
            self.label,
            self.summary,
            SYSTEM_ACTOR_ID if self.system_activity else self.actor_id,
            self.description)
