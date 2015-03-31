from opengever.activity import notification_center
from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.task.response_description import ResponseDescription
from plone import api
from Products.CMFPlone import PloneMessageFactory
from zope.i18n import translate


class TaskActivity(object):
    """The TaskActivity class is a representation for every activity which can be done with or
    on a task. It provides every needed attribute/methods to record the activity
    in the notification center.
    """

    def __init__(self, context, request, parent):
        self.context = context
        self.request = request
        self.parent = parent
        self.center = notification_center()

    @property
    def kind(self):
        raise NotImplementedError()

    @property
    def title(self):
        return self.context.title

    @property
    def actor_id(self):
        return api.user.get_current().getId()

    @property
    def summary(self):
        raise NotImplementedError()

    @property
    def description(self):
        raise NotImplementedError()

    def before_recording(self):
        """Will be called before adding the activity to the
        notification center (see method `record`). Used for watcher
        adjustments ect.
        """
        pass

    def after_recording(self):
        """Will be called after adding the activity to the
        notification center (see method `record`). Used for watcher
        adjustments ect.
        """
        pass

    def record(self):
        """Adds the activity itself to the notification center.
        """
        self.before_recording()

        self.center.add_activity(
            self.context, self.kind, self.title, self.summary,
            self.actor_id, description=self.description)

        self.after_recording()

    def translate(self, msg):
        return translate(msg, context=self.request)


class TaskAddedActivity(TaskActivity):
    """Activity representation for adding a task."""

    @property
    def kind(self):
        return PloneMessageFactory(u'task-added', default=u'Task added')

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('label_task_added', u'New task added by ${user}',
                mapping={'user': actor.get_label(with_principal=False)})
        return self.translate(msg)

    @property
    def description(self):
        return self.render_description_markup(self.collects_description_data())

    def render_description_markup(self, data):
        msg = u'<table><tbody>'
        for label, value in data:
            msg = u'{}<tr><th>{}</th><td>{}</td></tr>'.format(msg, label, value)

        return u'{}</tbody></table>'.format(msg)

    def collects_description_data(self):
        """Returns a list with [label, value] pairs.
        """
        return [
            [self.translate(_('label_task_title', u'Task title')),
             self.title],
            [self.translate(_('label_deadline', u'Deadline')),
             api.portal.get_localized_time(str(self.context.deadline))],
            [self.translate(_('label_task_type', u'Task Type')),
             self.context.get_task_type_label()],
            [self.translate(_('label_dossier_title', u'Dossier title')),
             self.parent.title],
            [self.translate(_('label_text', u'Text')),
             self.context.text]
        ]


    def before_recording(self):
        self.center.add_watcher_to_resource(self.context,
                                            self.context.responsible)
        self.center.add_watcher_to_resource(self.context,
                                            self.context.issuer)


class TaskTransitionActivity(TaskActivity):
    """Activity which represents a transition task transition change.
    """

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
        msg = ResponseDescription.get(response=self.response).msg()
        return self.translate(msg)

    @property
    def actor(self):
        return api.user.get_current().getId()

    @property
    def description(self):
        return self.response.text


class TaskReassignActivity(TaskTransitionActivity):
    """Updates the watcherlist for the current task because of the responsible
    change on the task.

    The issuer and the old and the new responsible should be notified.
    After recording the activity the old responsible should be removed from
    the watchers list.
    """

    def before_recording(self):
        """Adds new responsible to watchers list.
        """
        self.center.add_watcher_to_resource(self.context,
                                            self.context.responsible)

    def after_recording(self):
        """Remove old responsible from watchers list.
        """
        change = self.response.get_change('responsible')
        self.center.remove_watcher_from_resource(self.context,
                                                 change.get('before'))
