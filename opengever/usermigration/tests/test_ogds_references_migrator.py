from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.model.settings import NotificationSetting
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.ogds.models.user_settings import UserSettings
from opengever.testing import FunctionalTestCase
from opengever.usermigration.ogds_references import OGDSUserReferencesMigrator


class TestOGDSUserReferencesMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestOGDSUserReferencesMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

    def test_migrates_activity_actor_ids(self):
        resource = create(Builder('resource').oguid('client1:123'))
        activity = create(Builder('activity')
                          .having(resource=resource,
                                  actor_id='HANS.MUSTER'))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(activity)
        self.assertEquals('hans.muster', activity.actor_id)

    def test_migrates_watcher_actor_ids(self):
        watcher = create(Builder('watcher').having(actorid='HANS.MUSTER'))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(watcher)
        self.assertEquals('hans.muster', watcher.actorid)

    def test_migrates_notification_userids(self):
        resource = create(Builder('resource').oguid('client1:123'))
        activity = create(Builder('activity')
                          .having(resource=resource))

        notification = create(Builder('notification')
                              .having(activity=activity,
                                      userid='HANS.MUSTER', is_read=False))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(notification)
        self.assertEquals('hans.muster', notification.userid)

    def test_migrates_task_principals(self):
        ogds_task = create(Builder('globalindex_task')
                           .having(responsible='foo',
                                   principals=['HANS.MUSTER']))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(ogds_task)
        self.assertEquals(['hans.muster'], ogds_task.principals)

    def test_migrates_task_responsibles(self):
        ogds_task = create(Builder('globalindex_task')
                           .having(responsible='HANS.MUSTER'))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(ogds_task)
        self.assertEquals('hans.muster', ogds_task.responsible)

    def test_migrates_task_issuers(self):
        ogds_task = create(Builder('globalindex_task')
                           .having(issuer='HANS.MUSTER'))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(ogds_task)
        self.assertEquals('hans.muster', ogds_task.issuer)

    def test_migrates_user_settings(self):
        setting = UserSettings.save_setting_for_user(
            'HANS.MUSTER', 'notify_own_actions', True
        )
        # we migrate the primary key with a low-level query, flushing data here
        # prevents that we trip up sqlalchemy internals
        create_session().flush()

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        settings = UserSettings.query.all()
        self.assertEqual(1, len(settings))
        setting = settings[0]
        self.assertEqual(setting.userid, 'hans.muster')
        self.assertTrue(setting.notify_own_actions)

    def test_migrates_notification_settings(self):
        create(Builder('notification_setting')
               .having(kind='task-added-or-reassigned',
                       userid='HANS.MUSTER',
                       mail_notification_roles=[],
                       badge_notification_roles=[],
                       digest_notification_roles=[]))

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        settings = NotificationSetting.query.all()
        self.assertEqual(1, len(settings))
        setting = settings[0]
        self.assertEqual(setting.userid, 'hans.muster')

    def test_migrates_favorites(self):
        favorite = Favorite(
            oguid=Oguid.parse('fd:123'),
            userid='HANS.MUSTER',
            title=u'fixture fav 01',
            plone_uid='1234'
        )
        create_session().add(favorite)
        create_session().flush()

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(favorite)
        self.assertEqual(favorite.userid, 'hans.muster')

    def test_migrates_reminder_settings(self):
        task = create(Builder('task'))
        reminder = create(
            Builder('reminder_setting_model')
            .for_object(task)
            .having(actor_id='HANS.MUSTER')
        )

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(reminder)
        self.assertEqual('hans.muster', reminder.actor_id)

    def test_migrates_meeting_secretary(self):
        committee = create(Builder('committee_model'))
        meeting = create(Builder('meeting').having(
            committee=committee, secretary=self.old_ogds_user)
        )

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(meeting)
        self.assertEqual('hans.muster', meeting.secretary_id)

    def test_migrates_proposal_issuer(self):
        proposal = create(Builder('proposal_model').having(
            issuer='HANS.MUSTER')
        )

        OGDSUserReferencesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        create_session().refresh(proposal)
        self.assertEqual('hans.muster', proposal.issuer)
