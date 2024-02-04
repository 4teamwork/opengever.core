from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.security import elevated_privileges
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.resolve import LockingResolveManager
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestDossierTransfersPost(IntegrationTestCase):

    features = ('dossier-transfers', )

    def setUp(self):
        super(TestDossierTransfersPost, self).setUp()
        with elevated_privileges():
            self.add_participation(
                self.resolvable_dossier, u'meeting_user', ['final-drawing'])
            LockingResolveManager(self.resolvable_dossier).resolve()
            self.resolved_dossier = self.resolvable_dossier
            self.recipient = create(Builder('admin_unit')
                                    .id('recipient')
                                    .having(title='Remote Recipient'))

    def add_participation(self, dossier, participant_id, roles):
        handler = IParticipationAware(dossier)
        handler.add_participation(participant_id, roles)

    def create_test_payload(self, now):
        payload = {
            'title': 'Transfer Title',
            'message': 'Transfer Message',
            'expires': (now + timedelta(days=5)).isoformat(),
            'target': self.recipient.unit_id,
            'root': self.resolved_dossier.UID(),
            'documents': [self.resolvable_document.UID()],
            'participations': ['meeting_user'],
            'all_documents': False,
            'all_participations': False,
        }
        return payload.copy()

    @browsing
    def test_post_dossier_transfer(self, browser):
        self.login(self.regular_user, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        payload = self.create_test_payload(now)

        with freeze(now):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        self.assertEqual(201, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@dossier-transfers/1',
            u'@type': u'virtual.ogds.dossiertransfer',
            u'id': 1,
            u'title': u'Transfer Title',
            u'message': u'Transfer Message',
            u'created': u'2024-02-18T15:45:00+00:00',
            u'expires': u'2024-02-23T15:45:00+00:00',
            u'state': u'pending',
            u'source': get_current_admin_unit().unit_id,
            u'target': u'recipient',
            u'source_user': 'regular_user',
            u'root': u'createresolvabledossier000000001',
            u'documents': [u'createresolvabledossier000000003'],
            u'participations': [u'meeting_user'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_post_permissions(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        browser.open(self.portal, view='@dossier-transfers', method='POST',
                     data=json.dumps(payload),
                     headers=self.api_headers)

        # Guard assertion
        self.assertEqual(201, browser.status_code)

        # User is missing 'View' permission on the root dossier
        self.login(self.foreign_contributor, browser=browser)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)
        self.assertEqual('Unauthorized', browser.json['type'])

    @browsing
    def test_allow_same_unit_flag(self, browser):
        self.login(self.regular_user, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        payload = self.create_test_payload(now)

        payload['title'] = 'Transfer on same unit'
        payload['target'] = get_current_admin_unit().unit_id

        with freeze(now):
            with self.env(GEVER_DOSSIER_TRANSFERS_ALLOW_SAME_AU='1'):
                browser.open(self.portal, view='@dossier-transfers',
                             method='POST',
                             data=json.dumps(payload),
                             headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Transfer on same unit', browser.json['title'])
        self.assertEqual('plone', browser.json['source'])
        self.assertEqual('plone', browser.json['target'])

    @browsing
    def test_root_dossier_must_exist_and_be_resolved(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # Dossier must exist
        # (can't reasonably test this, because a nonexistent dossier will
        # already fail the permission check and result in a 401)

        # Dossier is not resolved
        payload['root'] = self.dossier.UID()
        payload['documents'] = [self.document.UID()]
        payload['all_participations'] = True
        payload.pop('participations')

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u'Inputs not valid',
            u'additional_metadata': {
                u'fields': [{
                    u'field': u'root',
                    u'translated_message': u'Root dossier with that UID does '
                                           u'not exist or is not resolved.',
                    u'type': u'InvalidRootDossier'},
                ],
            },
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_all_docs_and_docs_list_constraints(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # 'all_documents' and 'documents' are mutually exclusive
        payload['all_documents'] = True
        payload['documents'] = [self.resolvable_document.UID()]

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u"'all_documents == true' and "
                                   u"'documents' list are mutually exclusive.",
            u'additional_metadata': {},
        }
        self.assertDictContainsSubset(expected, browser.json)

        # 'documents' is required if 'all_documents' is False
        payload = self.create_test_payload(now)
        payload['all_documents'] = False
        payload.pop('documents')

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u"'documents' list is required "
                                   u"if 'all_documents' is false.",
            u'additional_metadata': {},
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_all_participations_and_participations_list_constraints(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # 'all_participations' and 'participations' are mutually exclusive
        payload['all_participations'] = True
        payload['participations'] = ['meeting_user']

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u"'all_participations == true' and "
                                   u"'participations' list are mutually exclusive.",
            u'additional_metadata': {},
        }
        self.assertDictContainsSubset(expected, browser.json)

        # 'participations' is required if 'all_participations' is False
        payload = self.create_test_payload(now)
        payload['all_participations'] = False
        payload.pop('participations')

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(payload),
                         headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u"'participations' list is required "
                                   u"if 'all_participations' is false.",
            u'additional_metadata': {},
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_expires_constraints(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # Expires must not be in the past
        payload['expires'] = (now - timedelta(days=5)).isoformat()

        with freeze(now):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.portal, view='@dossier-transfers', method='POST',
                             data=json.dumps(payload),
                             headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u'Inputs not valid',
            u'additional_metadata': {
                u'fields': [{
                    u'field': u'expires',
                    u'translated_message': u"'expires' must not be in the past.",
                    u'type': u'ExpiresInPast'},
                ],
            },
        }
        self.assertDictContainsSubset(expected, browser.json)

        # Expires must not be more than 30d in the future
        payload['expires'] = (now + timedelta(days=35)).isoformat()

        with freeze(now):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.portal, view='@dossier-transfers', method='POST',
                             data=json.dumps(payload),
                             headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u'Inputs not valid',
            u'additional_metadata': {
                u'fields': [{
                    u'field': u'expires',
                    u'translated_message': u"'expires' must not be more than "
                                           u"30 days in the future.",
                    u'type': u'ExpiresTooFarInFuture'},
                ],
            },
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_documents_list_constraints(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # Documents must be inside root dossier
        payload['documents'] = [self.meeting_document.UID()]

        with freeze(now):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.portal, view='@dossier-transfers', method='POST',
                             data=json.dumps(payload),
                             headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u'Inputs not valid',
            u'additional_metadata': {
                u'fields': [{
                    u'field': u'documents',
                    u'translated_message': u'Wrong contained type',
                    u'type': u'WrongContainedType'},
                ],
            },
        }
        self.assertDictContainsSubset(expected, browser.json)

    @browsing
    def test_participation_list_constraints(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        payload = self.create_test_payload(now)

        # Participations must exist on root dossier
        payload['participations'] = ['doesnt-exist']

        with freeze(now):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.portal, view='@dossier-transfers', method='POST',
                             data=json.dumps(payload),
                             headers=self.api_headers)

        expected = {
            u'type': u'BadRequest',
            u'translated_message': u'Inputs not valid',
            u'additional_metadata': {
                u'fields': [{
                    u'field': u'participations',
                    u'translated_message': u'Wrong contained type',
                    u'type': u'WrongContainedType'},
                ],
            },
        }
        self.assertDictContainsSubset(expected, browser.json)
