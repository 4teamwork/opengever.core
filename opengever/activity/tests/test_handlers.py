from opengever.activity.events import NotificationEvent
from opengever.activity.events import WatcherAddedEvent
from opengever.activity.model import Activity
from opengever.testing import IntegrationTestCase
from zope.event import notify


class TestNotificationEventHandler(IntegrationTestCase):

    features = (
        'activity',
    )

    def test_adds_new_activity(self):
        self.login(self.dossier_responsible)
        notify(NotificationEvent(
            self.task,
            'task-transition-open-in-progress',
            {'en': 'Task accepted'},
            {'en': 'Task accepted by Robert Ziegler.'},
            self.dossier_responsible,
            {'en': 'Lorem ipsum'},
        ))
        activity = Activity.query.first()
        self.assertEquals(self.task, activity.resource.oguid.resolve_object())
        self.assertEquals('task-transition-open-in-progress', activity.kind)
        self.assertEquals('Task accepted by Robert Ziegler.', activity.summary)
        self.assertEquals('Task accepted', activity.label)
        self.assertEquals('robert.ziegler', activity.actor_id)
        self.assertEquals('Lorem ipsum', activity.description)


class TestDisabledNotificationEventHandler(IntegrationTestCase):

    def test_event_is_ignored(self):
        self.login(self.dossier_responsible)
        notify(NotificationEvent(
            self.task,
            'task-transition-open-in-progress',
            'Task accepted.',
            self.dossier_responsible,
            'Lorem ipsum',
        ))
        self.assertEquals(0, Activity.query.count())


class TestWatcherAddedEventHandler(IntegrationTestCase):
    features = ('activity',)

    def test_adds_watcher_added_activity(self):
        self.login(self.regular_user)
        notify(WatcherAddedEvent(self.task.oguid, self.meeting_user.getId()))
        activity = Activity.query.first()
        self.assertEqual('task-watcher-added', activity.kind)
        self.assertEqual('Added as watcher of the task', activity.label)
        self.assertEqual('kathi.barfuss', activity.actor_id)
        self.assertEqual(u'Added as watcher of the task by <a href="http://nohost/plone/'
                         u'@@user-details/kathi.barfuss">B\xe4rfuss K\xe4thi (kathi.barfuss)</a>',
                         activity.summary)
