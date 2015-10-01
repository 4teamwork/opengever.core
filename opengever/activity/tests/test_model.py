from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.tests.base import ActivityTestCase


class TestNotification(ActivityTestCase):

    def test_string_representation(self):
        watcher = create(Builder('watcher').having(user_id=u'h\xfcgo.boss'))
        resource = create(Builder('resource').oguid('fd:123'))
        activity = create(Builder('activity').having(
            title=u'Bitte \xc4nderungen nachvollziehen', resource=resource))
        notification = create(Builder('notification')
                              .having(activity=activity, watcher=watcher))

        self.assertEqual(
            "<Notification 1 for <Watcher u'h\\xfcgo.boss'> on <Resource fd:123> >",
            str(notification))

        self.assertEqual(
            "<Notification 1 for <Watcher u'h\\xfcgo.boss'> on <Resource fd:123> >",
            repr(notification))


class TestWatcher(ActivityTestCase):

    def test_string_representation(self):
        watcher = create(Builder('watcher').having(user_id=u'h\xfcgo.boss'))

        self.assertEqual("<Watcher u'h\\xfcgo.boss'>", str(watcher))
        self.assertEqual("<Watcher u'h\\xfcgo.boss'>", repr(watcher))


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
        watcher = create(Builder('watcher').having(user_id=u'h\xfcgo.boss'))
        subscription = create(Builder('subscription')
                          .having(resource=resource, watcher=watcher))

        self.assertEqual(
            "<Subscription <Watcher u'h\\xfcgo.boss'> @ <Resource fd:123>>",
            str(subscription))
        self.assertEqual(
            "<Subscription <Watcher u'h\\xfcgo.boss'> @ <Resource fd:123>>",
            repr(subscription))

    def test_remove_role(self):
        resource = create(Builder('resource').oguid('fd:123'))
        watcher = create(Builder('watcher').having(user_id=u'h\xfcgo.boss'))
        subscription = create(Builder('subscription')
                          .having(resource=resource, watcher=watcher,
                                  roles=['watcher', 'issuer']))

        subscription.remove_role('watcher')

        self.assertEqual(['issuer'], subscription.roles)

    def test_remove_not_stored_role_is_ignored(self):
        resource = create(Builder('resource').oguid('fd:123'))
        watcher = create(Builder('watcher').having(user_id=u'h\xfcgo.boss'))
        subscription = create(Builder('subscription')
                          .having(resource=resource, watcher=watcher,
                                  roles=['watcher']))

        subscription.remove_role('issuer')
        self.assertEqual(['watcher'], subscription.roles)
