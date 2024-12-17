from ftw.builder import Builder
from ftw.builder import create
from opengever.activity import notification_center
from opengever.activity.sources import PossibleWatchersSource
from opengever.base.interfaces import IBaseSettings
from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.testing import IntegrationTestCase
from plone import api
from unittest import skip


class TestPossibleWatchersSource(IntegrationTestCase):

    features = ('activity', )

    def setUp(self):
        super(TestPossibleWatchersSource, self).setUp()
        self.login(self.administrator)

        # Remove all current subscriptions to get a clean state
        session = create_session()
        map(session.delete, notification_center().get_subscriptions(self.task))

    def test_list_users_groups_and_teams(self):
        self.login(self.regular_user)
        center = notification_center()
        source = PossibleWatchersSource(self.task)

        subscriptions = center.get_subscriptions(self.task)
        self.assertEqual([], [s.watcher.actorid for s in subscriptions])
        self.assertIn('regular_user', [term.token for term in source.search('')])
        self.assertIn('group:fa_users', [term.token for term in source.search('')])
        self.assertIn('team:1', [term.token for term in source.search('')])

    def test_respect_whitelist_groups_filter_for_possible_watchers(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        create(Builder('ogds_group').having(groupid='regular_group_1', title="Regular Group 1"))
        create(Builder('ogds_group').having(groupid='regular_group_2', title="Regular Group 2"))
        create(Builder('ogds_group').having(groupid='regular_group_3', title="Regular Group 3"))

        self.assertItemsEqual([
            'group:regular_group_1',
            'group:regular_group_2',
            'group:regular_group_3'
        ], [term.token for term in source.search('Regular Group')])

        api.portal.set_registry_record('possible_watcher_groups_white_list_regex', u'^.+2$', IBaseSettings)

        self.assertItemsEqual([
            'group:regular_group_2',
        ], [term.token for term in source.search('Regular Group')])

    def test_list_only_teams_assigned_to_the_current_org_unit(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        team_1 = create(Builder('ogds_team').having(title=u'Regular Team 1',
                                                    group=Group.query.first(),
                                                    org_unit=OrgUnit.get('fa')))

        create(Builder('ogds_team').having(title=u'Regular Team 2',
                                           group=Group.query.first(),
                                           org_unit=OrgUnit.get('fa')))

        create(Builder('ogds_team').having(title=u'Regular Team 3',
                                           group=Group.query.first(),
                                           org_unit=OrgUnit.get('fa')))

        self.assertItemsEqual([
            u'Regular Team 1 (Finanz\xe4mt)',
            u'Regular Team 2 (Finanz\xe4mt)',
            u'Regular Team 3 (Finanz\xe4mt)',
        ], [term.title for term in source.search('Regular Team')])

        team_1.org_unit = OrgUnit.get('rk')

        self.assertItemsEqual([
            u'Regular Team 2 (Finanz\xe4mt)',
            u'Regular Team 3 (Finanz\xe4mt)',
        ], [term.title for term in source.search('Regular Team')])

    def test_list_users_and_groups_for_teamraum(self):
        self.activate_feature('workspace')
        self.login(self.administrator)
        source = PossibleWatchersSource(self.task)

        self.assertIn('regular_user', [term.token for term in source.search('')])
        self.assertIn('group:fa_users', [term.token for term in source.search('')])
        self.assertNotIn('team:1', [term.token for term in source.search('')])

    def test_current_user_is_always_on_first_position_if_available(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.login(self.regular_user)
        self.assertEqual(self.regular_user.getId(), source.search('')[0].value)

        self.login(self.dossier_manager)
        self.assertEqual(self.dossier_manager.getId(), source.search('')[0].value)

        self.login(self.administrator)
        self.assertEqual(self.administrator.getId(), source.search('')[0].value)

    def test_filter_by_title_returns_the_filtered_results(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual(
            [
                'regular_user',
                'meeting_user',
                'committee.secretary',
                'service_user',
                'group:fa_inbox_users',
                'group:fa_users',
                'group:rk_inbox_users',
                'group:rk_users',
                'team:2',
                'team:3'
            ],
            [term.token for term in source.search('Se')])

    def test_search_is_case_insensitive(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual([
            self.workspace_owner.getId(),
            self.dossier_manager.getId(),
            self.workspace_admin.getId(),
            self.committee_responsible.getId()],
            [term.value for term in source.search('FR')])

    @skip('Vocabulary should be searchable by username, not (just) userid')
    def test_term_title_is_user_display_name(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)
        self.assertEqual(u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                         source.search(self.regular_user.getUserName())[0].title)

    def test_search_with_umlaut_works_properly(self):
        self.login(self.regular_user)
        source = PossibleWatchersSource(self.task)

        self.assertEqual(
            [self.regular_user.getId()],
            [term.value for term in source.search(u'B\xe4rfuss')])
