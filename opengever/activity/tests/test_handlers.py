from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.events import NotificationEvent
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from sqlalchemy import desc
from zope.event import notify


class TestNotificationEventHandler(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def test_adds_new_activity(self):
        task = create(Builder('task'))
        event = NotificationEvent(task,
                                  'task-transition-open-in-progress',
                                  {'en': 'Task accepted'},
                                  {'en': 'Task accepted by Test user.'},
                                  api.user.get_current(),
                                  {'en': 'Lorem ipsum'})
        notify(event)

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(task, activity.resource.oguid.resolve_object())
        self.assertEquals('task-transition-open-in-progress', activity.kind)
        self.assertEquals('Task accepted by Test user.', activity.summary)
        self.assertEquals('Task accepted', activity.label)
        self.assertEquals(TEST_USER_ID, activity.actor_id)
        self.assertEquals('Lorem ipsum', activity.description)


class TestDisabledNotificationEventHandler(FunctionalTestCase):

    def test_event_is_ignored(self):
        task = create(Builder('task'))
        event = NotificationEvent(task,
                                  'task-transition-open-in-progress',
                                  'Task accepted.',
                                  api.user.get_current(),
                                  'Lorem ipsum')
        notify(event)

        self.assertEquals(0, Activity.query.count())
