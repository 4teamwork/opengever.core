from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import FunctionalTestCase


class TestWatcher(FunctionalTestCase):

    def test_string_representation(self):
        watcher = create(Builder('watcher').having(actorid=u'h\xfcgo.boss'))

        self.assertEqual("<Watcher u'h\\xfcgo.boss'>", str(watcher))
        self.assertEqual("<Watcher u'h\\xfcgo.boss'>", repr(watcher))

    def test_get_user_ids_returns_userid_for_user_watcher(self):
        create(Builder('ogds_user').id(u'hugo.boss'))
        watcher = create(Builder('watcher').having(actorid=u'hugo.boss'))
        self.assertEqual(['hugo.boss'], watcher.get_user_ids())

    def test_get_user_ids_returns_userids_of_inbox_group_users_for_inbox_watcher(self):
        hugo = create(Builder('ogds_user').id(u'hugo.boss'))
        peter = create(Builder('ogds_user').id(u'peter.michel'))
        james = create(Builder('ogds_user').id(u'james.bond'))

        create(Builder('admin_unit').id('fd'))
        create(Builder('org_unit')
               .id('fd')
               .having(admin_unit_id='fd')
               .assign_users([hugo, peter])
               .assign_users([james], to_inbox=False))

        watcher = create(Builder('watcher').having(actorid=u'inbox:fd'))
        self.assertEqual(['hugo.boss', 'peter.michel'],
                         watcher.get_user_ids())

    def test_get_user_ids_for_inbox_watcher_ignores_users_with_inbox_notifications_disabled(self):
        hugo = create(Builder('ogds_user').id(u'hugo.boss'))
        peter = create(Builder('ogds_user').id(u'peter.michel'))
        james = create(Builder('ogds_user').id(u'james.bond'))

        UserSettings.save_setting_for_user(peter.userid, 'notify_inbox_actions', False)

        create(Builder('admin_unit').id('fd'))
        create(Builder('org_unit')
               .id('fd')
               .having(admin_unit_id='fd')
               .assign_users([hugo, peter, james]))

        watcher = create(Builder('watcher').having(actorid=u'inbox:fd'))
        self.assertEqual(['hugo.boss', 'james.bond'],
                         watcher.get_user_ids())

    def test_get_user_ids_returns_userids_of_group_users_for_group_watcher(self):
        group_id = 'informed_users'
        group = create(Builder('ogds_group').having(groupid=group_id))

        create(Builder('ogds_user').id(u'hugo.boss').in_group(group))
        create(Builder('ogds_user').id(u'peter.michel').in_group(group))
        create(Builder('ogds_user').id(u'james.bond'))

        watcher = create(Builder('watcher').having(actorid=group_id))
        self.assertEqual(['hugo.boss', 'peter.michel'],
                         watcher.get_user_ids())

    def test_get_user_ids_returns_userids_of_team_users_for_team_watcher(self):
        create(Builder('admin_unit').id('fd'))

        orgunit = create(Builder('org_unit').id('fd').having(
          admin_unit_id='fd'))

        group = create(Builder('ogds_group').having(
          groupid='informed_users'))

        team = create(Builder('ogds_team').having(
          group=group,
          title='Test Team',
          org_unit=orgunit))

        create(Builder('ogds_user').id(u'hugo.boss').in_group(group))
        create(Builder('ogds_user').id(u'peter.michel').in_group(group))
        create(Builder('ogds_user').id(u'james.bond'))

        actorid = 'team:{}'.format(team.team_id)
        watcher = create(Builder('watcher').having(actorid=actorid))
        self.assertEqual(['hugo.boss', 'peter.michel'],
                         watcher.get_user_ids())
