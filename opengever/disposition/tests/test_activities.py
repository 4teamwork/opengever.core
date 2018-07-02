from ftw.builder import Builder
from ftw.builder import create
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.model import Resource
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.actor import Actor
from opengever.testing import FunctionalTestCase
from plone import api
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
        self.actor_link = Actor.lookup(TEST_USER_ID).get_link()

    def test_creator_and_all_archivist_are_registered_as_watchers(self):
        acl_users = api.portal.get_tool('acl_users')
        role_manager = acl_users.get('portal_role_manager')
        role_manager.assignRoleToPrincipal(
            'Archivist', self.org_unit.inbox_group.groupid)

        create(Builder('ogds_user')
               .id('peter.meier')
               .having(firstname='peter', lastname='meier',
                       email='meier@example.com')
               .assign_to_org_units([self.org_unit])
               .in_group(self.org_unit.inbox_group))

        create(Builder('disposition'))

        resource = Resource.query.one()

        archivist_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_ARCHIVIST_ROLE]
        records_manager_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_RECORDS_MANAGER_ROLE]

        self.assertItemsEqual([TEST_USER_ID], records_manager_watchers)
        self.assertItemsEqual(
            [TEST_USER_ID, u'hugo.boss', u'hans.boss', u'peter.meier'],
            archivist_watchers)

    def test_added_activity_is_recorded_when_a_disposition_is_created(self):
        create(Builder('disposition').titled(u'Angebot 13.49'))

        activity = Activity.query.one()
        self.assertEquals('disposition-added', activity.kind)
        self.assertEquals(
            u'New disposition added by Test User on admin unit Admin Unit 1',
            activity.summary)
        self.assertEquals(u'Disposition added', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Angebot 13.49', activity.title)

    def test_appraise_activity_is_recorded(self):
        self.grant('Archivist')
        disposition = create(Builder('disposition'))
        api.content.transition(disposition,
                               transition='disposition-transition-appraise')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-appraise', activity.kind)
        self.assertEquals(
            u'Appraisal finalized by {}'.format(self.actor_link),
            activity.summary)
        self.assertEquals(u'disposition-transition-appraise', activity.label)
        self.assertIsNone(activity.description)

    def test_dispose_activity_is_recorded(self):
        self.grant('Records Manager')
        dossier = create(Builder('dossier')
                         .as_expired()
                         .having(archival_value=ARCHIVAL_VALUE_WORTHY))

        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier])
                             .in_state('disposition-state-appraised'))
        api.content.transition(disposition,
                               transition='disposition-transition-dispose')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-dispose', activity.kind)
        self.assertEquals(
            u'Disposition disposed for the archive by {}'.format(self.actor_link),
            activity.summary)
        self.assertEquals(u'disposition-transition-dispose', activity.label)
        self.assertIsNone(activity.description)

    def test_appraised_to_close_activity_is_recorded(self):
        self.grant('Records Manager')
        dossier = create(Builder('dossier')
                         .as_expired()
                         .having(archival_value=ARCHIVAL_VALUE_UNWORTHY))
        disposition = create(Builder('disposition')
                             .having(dossiers=[dossier])
                             .in_state('disposition-state-appraised'))
        api.content.transition(disposition,
                               transition='disposition-transition-appraised-to-closed')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-appraised-to-closed', activity.kind)
        self.assertEquals(
            u'Disposition closed and all dossiers destroyed by {}'.format(
                self.actor_link),
            activity.summary)
        self.assertEquals(u'disposition-transition-appraised-to-closed', activity.label)
        self.assertIsNone(activity.description)

    def test_archive_activity_is_recorded(self):
        self.grant('Archivist')
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))
        api.content.transition(disposition,
                               transition='disposition-transition-archive')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-archive', activity.kind)
        self.assertEquals(
            u'The archiving confirmed by {}'.format(self.actor_link),
            activity.summary)
        self.assertEquals(u'disposition-transition-archive', activity.label)
        self.assertIsNone(activity.description)

    def test_close_activity_is_recorded(self):
        self.grant('Records Manager')
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-archived'))
        api.content.transition(disposition,
                               transition='disposition-transition-close')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-close', activity.kind)
        self.assertEquals(
            u'Disposition closed and all dossiers '
            'destroyed by {}'.format(self.actor_link), activity.summary)
        self.assertEquals(u'disposition-transition-close', activity.label)
        self.assertIsNone(activity.description)

    def test_refuse_activity_is_recorded(self):
        self.grant('Archivist')
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))
        api.content.transition(disposition,
                               transition='disposition-transition-refuse')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-refuse', activity.kind)
        self.assertEquals(
            u'Disposition refused by {}'.format(self.actor_link),
            activity.summary)
        self.assertEquals(u'disposition-transition-refuse', activity.label)
        self.assertIsNone(activity.description)
