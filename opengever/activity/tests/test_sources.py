from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.sources import PossibleWatchersSource
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase


class TestPossibleWatchersSource(IntegrationTestCase):

    features = ('activity', )

    def setUp(self):
        super(TestPossibleWatchersSource, self).setUp()
        self.login(self.administrator)

        # Remove all current subscriptions to get a clean state
        session = create_session()
        map(session.delete, notification_center().get_subscriptions(self.task))

    def test_list_users_not_having_a_watcher_role_on_an_object(self):
        self.login(self.regular_user)
        center = notification_center()
        source = PossibleWatchersSource(self.task)

        subscriptions = center.get_subscriptions(self.task)
        self.assertEqual([], [s.watcher.actorid for s in subscriptions])
        self.assertIn(u'kathi.barfuss', [term.value for term in source.search('')])

        center.add_watcher_to_resource(self.task, self.regular_user.getId(), WATCHER_ROLE)

        subscriptions = center.get_subscriptions(self.task)
        self.assertEqual(['kathi.barfuss'], [s.watcher.actorid for s in subscriptions])
        self.assertNotIn(u'kathi.barfuss', [term.value for term in source.search('')])

    def test_current_user_is_always_on_first_position_if_available(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.login(self.regular_user)
        self.assertEqual(self.regular_user.getId(), source.search('')[0].value)

        self.login(self.dossier_manager)
        self.assertEqual(self.dossier_manager.getId(), source.search('')[0].value)

        self.login(self.administrator)
        self.assertEqual(self.administrator.getId(), source.search('')[0].value)

    def test_filter_by_title_returns_the_filtered_users(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual([
            u'gunther.frohlich',
            u'faivel.fruhling',
            u'fridolin.hugentobler',
            u'franzi.muller'],
            [term.value for term in source.search('fr')])

    def test_search_is_case_insensitive(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual([
            u'gunther.frohlich',
            u'faivel.fruhling',
            u'fridolin.hugentobler',
            u'franzi.muller'],
            [term.value for term in source.search('FR')])

    def test_term_title_is_user_display_name(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)
        self.assertEqual(u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                         source.search('kathi.barfuss')[0].title)

    def test_search_with_umlaut_works_properly(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual(
            [self.regular_user.getId()],
            [term.value for term in source.search(u'B\xe4rfuss')])
