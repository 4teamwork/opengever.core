from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.security import elevated_privileges
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
            LockingResolveManager(self.resolvable_dossier).resolve()
            self.resolved_dossier = self.resolvable_dossier
            self.recipient = create(Builder('admin_unit')
                                    .id('recipient')
                                    .having(title='Remote Recipient'))

    @browsing
    def test_post_dossier_transfer(self, browser):
        self.login(self.regular_user, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            data = {
                'title': 'Transfer Title',
                'message': 'Transfer Message',
                'expires': (now + timedelta(days=5)).isoformat(),
                'target': self.recipient.unit_id,
                'root': self.resolved_dossier.UID(),
                'documents': [self.document.UID()],
                'participations': ['p1'],
                'all_documents': False,
                'all_participations': False,
            }

            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(data),
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
            u'documents': [u'createtreatydossiers000000000002'],
            u'participations': [u'p1'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_post_permissions(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        expires = now + timedelta(days=5)

        data = {
            'title': 'Transfer Title',
            'message': 'Transfer Message',
            'expires': expires.isoformat(),
            'target': self.recipient.unit_id,
            'root': self.resolved_dossier.UID(),
            'documents': [self.document.UID()],
            'participations': ['p1'],
            'all_documents': False,
            'all_participations': False,
        }

        browser.open(self.portal, view='@dossier-transfers', method='POST',
                     data=json.dumps(data),
                     headers=self.api_headers)

        # Guard assertion
        self.assertEqual(201, browser.status_code)

        # User is missing 'View' permission on the root dossier
        self.login(self.foreign_contributor, browser=browser)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(data),
                         headers=self.api_headers)
        self.assertEqual('Unauthorized', browser.json['type'])

    @browsing
    def test_allow_same_unit_flag(self, browser):
        self.login(self.regular_user, browser=browser)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            data = {
                'title': 'Transfer on same unit',
                'expires': (now + timedelta(days=5)).isoformat(),
                'target': get_current_admin_unit().unit_id,
                'root': self.resolved_dossier.UID(),
                'documents': [self.document.UID()],
                'participations': ['p1'],
                'all_documents': False,
                'all_participations': False,
            }

            with self.env(GEVER_DOSSIER_TRANSFERS_ALLOW_SAME_AU='1'):
                browser.open(self.portal, view='@dossier-transfers',
                             method='POST',
                             data=json.dumps(data),
                             headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual('Transfer on same unit', browser.json['title'])
        self.assertEqual('plone', browser.json['source'])
        self.assertEqual('plone', browser.json['target'])

    @browsing
    def test_root_dossier_must_exist_and_be_resolved(self, browser):
        self.login(self.regular_user, browser=browser)

        now = utcnow_tz_aware()
        expires = now + timedelta(days=5)

        metadata = {
            'title': 'Transfer Title',
            'message': 'Transfer Message',
            'expires': expires.isoformat(),
            'target': self.recipient.unit_id,
            'documents': [self.document.UID()],
            'participations': ['p1'],
            'all_documents': False,
            'all_participations': False,
        }

        # Dossier must exist
        # (can't reasonably test this, because a nonexistent dossier will
        # already fail the permission check and result in a 401)

        # Dossier is not resolved
        data = metadata.copy()
        data['root'] = self.dossier.UID()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal, view='@dossier-transfers', method='POST',
                         data=json.dumps(data),
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
