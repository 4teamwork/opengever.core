from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.model import Activity
from opengever.activity.model import Resource
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.oguid import Oguid
from opengever.disposition.nightly_jobs import NightlyDossierPermissionSetter
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from plone import api
import logging


class TestDispositionNotifications(IntegrationTestCase):

    features = ('activity', )

    def run_nightly_jobs(self, expected):
        logger = logging.getLogger('opengever.nightlyjobs')
        logger.addHandler(logging.NullHandler())
        nightly_job_provider = NightlyDossierPermissionSetter(
            self.portal, self.request, logger)
        jobs = list(nightly_job_provider)
        self.assertEqual(expected, len(jobs))
        for job in jobs:
            nightly_job_provider.run_job(job, lambda: False)

    def test_creator_and_all_archivist_are_registered_as_watchers(self):
        self.login(self.manager)
        self.disposition.dossiers_with_missing_permissions = []
        self.disposition_with_sip.dossiers_with_missing_permissions = []
        disposition = create(Builder('disposition').having(dossiers=[self.expired_dossier]))
        self.run_nightly_jobs(expected=1)
        resource = Resource.query.get_by_oguid(Oguid.for_object(disposition))

        archivist_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_ARCHIVIST_ROLE]
        records_manager_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == DISPOSITION_RECORDS_MANAGER_ROLE]

        self.assertItemsEqual([self.manager.getId()], records_manager_watchers)
        self.assertItemsEqual([self.archivist.getId()], archivist_watchers)

    def test_added_activity_is_recorded_after_permissions_are_set(self):
        self.login(self.manager)
        self.disposition.dossiers_with_missing_permissions = []
        self.disposition_with_sip.dossiers_with_missing_permissions = []

        actor = ActorLookup(self.manager.getId()).lookup()
        disposition = create(Builder('disposition')
                             .titled(u'Angebot 13.49')
                             .having(dossiers=[self.expired_dossier]))
        self.assertFalse(disposition.creation_activity_recorded)
        self.assertEquals(0, Activity.query.count())

        self.run_nightly_jobs(expected=1)

        activity = Activity.query.one()
        self.assertEquals('disposition-added', activity.kind)
        self.assertEquals(
            u'New offer added by {} on admin unit Hauptmandant'.format(
                actor.get_label(with_principal=False)),
            activity.summary)
        self.assertEquals(u'Offer added', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Angebot 13.49', activity.title)

        self.assertTrue(disposition.creation_activity_recorded)

        # Activity should only be created once and not when dossiers is modified.
        disposition.dossiers = []
        self.run_nightly_jobs(expected=1)
        self.assertEqual(1, Activity.query.count())

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
        self.assertEquals(u'Appraise disposition', activity.label)
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
            u'Offered for archival by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'Submit disposition', activity.label)
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
            u'Offer closed and all dossiers destroyed by {}'.format(
                actor.get_link()),
            activity.summary)
        self.assertEquals(u'Dispose of dossiers', activity.label)
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
            u'Archival confirmed by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'Confirm archival', activity.label)
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
            u'Offer closed and all dossiers '
            'destroyed by {}'.format(actor.get_link()), activity.summary)
        self.assertEquals(u'Dispose of dossiers', activity.label)
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
            u'Offer refused by {}'.format(actor.get_link()),
            activity.summary)
        self.assertEquals(u'Refuse', activity.label)
        self.assertIsNone(activity.description)
