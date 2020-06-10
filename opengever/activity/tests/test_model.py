from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.model.notification import Notification
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.tests.base import ActivityTestCase
from sqlalchemy.exc import IntegrityError
import transaction


class TestNotification(ActivityTestCase):

    def test_string_representation(self):
        resource = create(Builder('resource').oguid('fd:123'))
        activity = create(Builder('activity').having(
            title=u'Bitte \xc4nderungen nachvollziehen', resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, userid=u'h\xfcgo.boss'))

        self.assertEqual(
            "<Notification 1 for u'h\\xfcgo.boss' on <Resource fd:123> >",
            str(notification))

        self.assertEqual(
            "<Notification 1 for u'h\\xfcgo.boss' on <Resource fd:123> >",
            repr(notification))

    def test_by_subscription_role_query(self):
        resource = create(Builder('resource').oguid('fd:123'))
        activity = create(Builder('activity').having(
            title=u'Bitte \xc4nderungen nachvollziehen', resource=resource))

        create(Builder('ogds_user').id(u'h\xfcgo'))
        create(Builder('ogds_user').id('peter'))
        hugo = create(Builder('watcher').having(actorid=u'h\xfcgo'))
        peter = create(Builder('watcher').having(actorid=u'peter'))

        create(Builder('subscription').having(resource=resource,
                                              watcher=peter,
                                              role=TASK_ISSUER_ROLE))
        create(Builder('subscription').having(resource=resource,
                                              watcher=peter,
                                              role=WATCHER_ROLE))
        create(Builder('subscription').having(resource=resource,
                                              watcher=hugo,
                                              role=WATCHER_ROLE))

        notification_1 = create(Builder('notification')
                                .having(activity=activity, userid=u'h\xfcgo'))
        notification_2 = create(Builder('notification')
                                .having(activity=activity, userid=u'peter'))

        notifications = Notification.query.by_subscription_roles(
            [TASK_ISSUER_ROLE], activity).all()
        self.assertEqual([notification_2], notifications)

        notifications = Notification.query.by_subscription_roles(
            [WATCHER_ROLE], activity).all()
        self.assertItemsEqual([notification_1, notification_2], notifications)

        notifications = Notification.query.by_subscription_roles(
            [TASK_RESPONSIBLE_ROLE], activity).all()
        self.assertEqual([], notifications)

    def test_unsent_digest_notifications(self):
        resource = create(Builder('resource').oguid('fd:123'))
        activity1 = create(Builder('activity')
                           .having(title=u'Bitte \xc4nderungen nachvollziehen',
                                   resource=resource))

        create(Builder('notification')
               .having(activity=activity1, userid=u'h\xfcgo',
                       is_digest=False))
        create(Builder('notification')
               .having(activity=activity1, userid=u'peter',
                       is_digest=True, sent_in_digest=True))
        note3 = create(Builder('notification')
                       .having(activity=activity1, userid=u'peter',
                               is_digest=True, sent_in_digest=False))

        self.assertEqual(
            [note3],
            Notification.query.unsent_digest_notifications().all())


class TestResource(ActivityTestCase):

    def test_string_representation(self):
        resource = create(Builder('resource').oguid('fd:123'))

        self.assertEqual("<Resource fd:123>", str(resource))
        self.assertEqual("<Resource fd:123>", repr(resource))


class TestActivity(ActivityTestCase):

    def test_string_representation(self):
        resource = create(Builder('resource').oguid('fd:123'))
        activity = create(Builder('activity').having(
            title=u'Bitte \xc4nderungen nachvollziehen',
            kind=u'task-added',
            resource=resource))

        self.assertEqual("<Activity task-added on <Resource fd:123> >",
                         str(activity))
        self.assertEqual("<Activity task-added on <Resource fd:123> >",
                         repr(activity))


class TestSubscription(ActivityTestCase):

    def test_string_representation(self):
        resource = create(Builder('resource').oguid('fd:123'))
        watcher = create(Builder('watcher').having(actorid=u'h\xfcgo.boss'))
        subscription = create(Builder('subscription')
                              .having(resource=resource,
                                      watcher=watcher,
                                      role=WATCHER_ROLE))

        self.assertEqual(
            "<Subscription <Watcher u'h\\xfcgo.boss'> @ <Resource fd:123>>",
            str(subscription))
        self.assertEqual(
            "<Subscription <Watcher u'h\\xfcgo.boss'> @ <Resource fd:123>>",
            repr(subscription))

    def test_primary_key_definition(self):
        resource = create(Builder('resource').oguid('fd:123'))
        watcher = create(Builder('watcher').having(actorid=u'h\xfcgo.boss'))
        create(Builder('subscription')
               .having(resource=resource, watcher=watcher, role=WATCHER_ROLE))

        with self.assertRaises(IntegrityError):
            create(Builder('subscription')
                   .having(resource=resource,
                           watcher=watcher,
                           role=WATCHER_ROLE))
            transaction.commit()

        transaction.abort()
