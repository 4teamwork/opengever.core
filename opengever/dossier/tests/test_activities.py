from opengever.activity import notification_center
from opengever.activity import SYSTEM_ACTOR_ID
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.dossier.activities import DossierOverdueActivity
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase


class TestDossierOverdueActivity(IntegrationTestCase):

    features = ('activity', )

    def _get_watcher_ids(self, obj):
        watchers = notification_center().get_watchers(self.dossier)
        return [watcher.actorid for watcher in watchers]

    def test_dossier_overdue_activity_is_from_system_user(self):
        self.login(self.dossier_manager)
        DossierOverdueActivity(self.dossier, self.request).record()
        activity = Activity.query.filter(
            Activity.kind == DossierOverdueActivity.kind).first()

        self.assertEqual(SYSTEM_ACTOR_ID, activity.actor_id)

    def test_register_resonsible_as_watcher_on_activity_creation(self):
        self.login(self.dossier_manager)
        IDossier(self.dossier).responsible = self.regular_user.getId()
        DossierOverdueActivity(self.dossier, self.request).record()

        activity_query = Activity.query.filter(
            Activity.kind == DossierOverdueActivity.kind)

        self.assertEqual(1, activity_query.count())

        notifications = activity_query.first().notifications
        self.assertEqual(
            [self.regular_user.getId()],
            [notification.userid for notification in notifications])

    def test_update_dossier_overdue_watcher_on_activity_recreation(self):
        self.login(self.dossier_manager)

        self.assertEqual([], self._get_watcher_ids(self.dossier))

        IDossier(self.dossier).responsible = self.regular_user.getId()
        DossierOverdueActivity(self.dossier, self.request).record()

        self.assertEqual([self.regular_user.getId()],
                         self._get_watcher_ids(self.dossier))
        self.assertEqual(1, Notification.query.count())

        IDossier(self.dossier).responsible = self.dossier_manager.getId()
        DossierOverdueActivity(self.dossier, self.request).record()

        self.assertEqual([self.dossier_manager.getId()],
                         self._get_watcher_ids(self.dossier))
        self.assertEqual(2, Notification.query.count())
