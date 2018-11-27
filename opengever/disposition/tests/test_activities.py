from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.model import Activity
from opengever.activity.model import Resource
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from plone import api


class TestDispositionNotifications(IntegrationTestCase):

    features = ('activity', )

    def test_creator_and_all_archivist_are_registered_as_watchers(self):
        self.login(self.regular_user)
        create(Builder('disposition'))

        resource = Resource.query.one()

        archivist_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_ARCHIVIST_ROLE]
        records_manager_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_RECORDS_MANAGER_ROLE]

        self.assertItemsEqual([self.regular_user.getId()], records_manager_watchers)
        self.assertItemsEqual([self.archivist.getId()], archivist_watchers)

    def test_added_activity_is_recorded_when_a_disposition_is_created(self):
        self.login(self.regular_user)
        actor = ActorLookup(self.regular_user.getId()).lookup()
        create(Builder('disposition').titled(u'Angebot 13.49'))

        activity = Activity.query.one()
        self.assertEquals('disposition-added', activity.kind)
        self.assertEquals(
            u'New disposition added by {} on admin unit Hauptmandant'.format(
                actor.get_label(with_principal=False)),
            activity.summary)
        self.assertEquals(u'Disposition added', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Angebot 13.49', activity.title)

    def test_appraise_activity_is_recorded(self):
        self.login(self.archivist)
        actor = ActorLookup(self.archivist.getId()).lookup()
        disposition = create(Builder('disposition'))
        api.content.transition(disposition,
                               transition='disposition-transition-appraise')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-appraise', activity.kind)
        self.assertEquals(
            u'Appraisal finalized by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'disposition-transition-appraise', activity.label)
        self.assertIsNone(activity.description)

    def test_dispose_activity_is_recorded(self):
        self.login(self.records_manager)
        actor = ActorLookup(self.records_manager.getId()).lookup()
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_WORTHY

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.expired_dossier])
                             .in_state('disposition-state-appraised'))
        api.content.transition(disposition,
                               transition='disposition-transition-dispose')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-dispose', activity.kind)
        self.assertEquals(
            u'Disposition disposed for the archive by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'disposition-transition-dispose', activity.label)
        self.assertIsNone(activity.description)

    def test_appraised_to_close_activity_is_recorded(self):
        self.login(self.records_manager)
        actor = ActorLookup(self.records_manager.getId()).lookup()
        ILifeCycle(self.expired_dossier).archival_value = ARCHIVAL_VALUE_UNWORTHY

        disposition = create(Builder('disposition')
                             .having(dossiers=[self.expired_dossier])
                             .in_state('disposition-state-appraised'))
        api.content.transition(disposition,
                               transition='disposition-transition-appraised-to-closed')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-appraised-to-closed', activity.kind)
        self.assertEquals(
            u'Disposition closed and all dossiers destroyed by {}'.format(
                actor.get_link()),
            activity.summary)
        self.assertEquals(u'disposition-transition-appraised-to-closed', activity.label)
        self.assertIsNone(activity.description)

    def test_archive_activity_is_recorded(self):
        self.login(self.archivist)
        actor = ActorLookup(self.archivist.getId()).lookup()
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))
        api.content.transition(disposition,
                               transition='disposition-transition-archive')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-archive', activity.kind)
        self.assertEquals(
            u'The archiving confirmed by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'disposition-transition-archive', activity.label)
        self.assertIsNone(activity.description)

    def test_close_activity_is_recorded(self):
        self.login(self.records_manager)
        actor = ActorLookup(self.records_manager.getId()).lookup()
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-archived'))
        api.content.transition(disposition,
                               transition='disposition-transition-close')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-close', activity.kind)
        self.assertEquals(
            u'Disposition closed and all dossiers '
            'destroyed by {}'.format(actor.get_link()), activity.summary)
        self.assertEquals(u'disposition-transition-close', activity.label)
        self.assertIsNone(activity.description)

    def test_refuse_activity_is_recorded(self):
        self.login(self.archivist)
        actor = ActorLookup(self.archivist.getId()).lookup()
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))
        api.content.transition(disposition,
                               transition='disposition-transition-refuse')

        activity = Activity.query.all()[-1]
        self.assertEquals('disposition-transition-refuse', activity.kind)
        self.assertEquals(
            u'Disposition refused by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'disposition-transition-refuse', activity.label)
        self.assertIsNone(activity.description)
