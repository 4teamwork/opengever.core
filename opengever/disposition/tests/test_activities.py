from ftw.builder import Builder
from ftw.builder import create
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.model import Resource
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestDispositionNotifications(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestDispositionNotifications, self).setUp()

        self.hugo = create(Builder('user')
                           .named('Hugo', 'Boss')
                           .with_roles('Contributor', 'Archivist'))
        self.peter = create(Builder('user')
                            .named('Peter', 'Boss')
                            .with_roles('Contributor'))
        self.hans = create(Builder('user')
                           .named('Hans', 'Boss')
                           .with_roles('Contributor', 'Archivist'))

        self.center = notification_center()

    def test_creator_and_all_archivist_are_registered_as_watchers(self):
        create(Builder('disposition'))

        resource = Resource.query.one()
        self.assertItemsEqual(
            [TEST_USER_ID, u'hugo.boss', u'hans.boss'],
            [watcher.actorid for watcher in resource.watchers])

    def test_added_activity_is_recorded_when_a_disposition_is_created(self):
        disposition = create(Builder('disposition').titled(u'Angebot 13.49'))

        activity = Activity.query.one()
        self.assertEquals('disposition-added', activity.kind)
        self.assertEquals(
            u'New disposition added by Test User on admin unit Client1',
            activity.summary)
        self.assertEquals(u'Disposition added', activity.label)
        self.assertEquals(None, activity.description)
        self.assertEquals(u'Angebot 13.49', activity.title)
