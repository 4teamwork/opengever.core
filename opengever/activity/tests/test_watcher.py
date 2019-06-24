from ftw.builder import Builder
from ftw.builder import create
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
        peter = create(Builder('ogds_user').id(u'peter.michel')
                       .having(notify_inbox_actions=False))
        james = create(Builder('ogds_user').id(u'james.bond'))

        create(Builder('admin_unit').id('fd'))
        create(Builder('org_unit')
               .id('fd')
               .having(admin_unit_id='fd')
               .assign_users([hugo, peter, james]))

        watcher = create(Builder('watcher').having(actorid=u'inbox:fd'))
        self.assertEqual(['hugo.boss', 'james.bond'],
                         watcher.get_user_ids())
