from opengever.activity.events import NotificationEvent
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
