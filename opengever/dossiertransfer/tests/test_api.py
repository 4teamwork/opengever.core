from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestDossierTransfersPost(IntegrationTestCase):

    features = ('dossier-transfers', )

    @browsing
    def test_post_dossier_transfer(self, browser):
        self.login(self.manager, browser=browser)

        recipient = create(Builder('admin_unit')
                           .id('recipient')
                           .having(title='Remote Recipient'))

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            data = {
                'title': 'Transfer Title',
                'message': 'Transfer Message',
                'expires': (now + timedelta(days=5)).isoformat(),
                'target': recipient.unit_id,
                'root': self.dossier.UID(),
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
            u'source_user': None,
            u'root': u'createtreatydossiers000000000001',
            u'documents': [u'createtreatydossiers000000000002'],
            u'participations': [u'p1'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)


class TestDossierTransfersGet(IntegrationTestCase):

    features = ('dossier-transfers', )

    @browsing
    def test_get_dossier_transfer(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()

        browser.open(self.portal, view='@dossier-transfers/%s' % transfer.id,
                     method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@dossier-transfers/1',
            u'@type': u'virtual.ogds.dossiertransfer',
            u'id': 1,
            u'title': u'Transfer Title',
            u'message': u'Transfer Message',
            u'created': u'2024-02-18T15:45:00+00:00',
            u'expires': u'2024-03-19T15:45:00+00:00',
            u'state': u'pending',
            u'source': u'plone',
            u'target': u'recipient',
            u'source_user': u'regular_user',
            u'root': u'createtreatydossiers000000000001',
            u'documents': [u'createtreatydossiers000000000002'],
            u'participations': [u'p1'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_get_dossier_transfer_listing(self, browser):
        self.login(self.manager, browser=browser)

        recipient = create(Builder('admin_unit')
                           .id('recipient')
                           .having(title='Remote Recipient'))

        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            transfer1 = create(Builder('dossier_transfer')
                               .with_target(recipient))
            transfer2 = create(Builder('dossier_transfer')
                               .with_target(recipient)
                               .having(title='Transfer 2'))
            session = create_session()
            session.add(transfer1)
            session.add(transfer2)
            session.flush()

        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@dossier-transfers',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@dossier-transfers/1',
                    u'@type': u'virtual.ogds.dossiertransfer',
                    u'id': 1,
                    u'title': u'Transfer Title',
                    u'message': u'Transfer Message',
                    u'created': u'2024-02-18T15:45:00+00:00',
                    u'expires': u'2024-03-19T15:45:00+00:00',
                    u'state': u'pending',
                    u'source': u'plone',
                    u'target': u'recipient',
                    u'source_user': u'regular_user',
                    u'root': u'createtreatydossiers000000000001',
                    u'documents': [u'createtreatydossiers000000000002'],
                    u'participations': [u'p1'],
                    u'all_documents': False,
                    u'all_participations': False,
                },
                {
                    u'@id': u'http://nohost/plone/@dossier-transfers/2',
                    u'@type': u'virtual.ogds.dossiertransfer',
                    u'id': 2,
                    u'title': u'Transfer 2',
                    u'message': u'Transfer Message',
                    u'created': u'2024-02-18T15:45:00+00:00',
                    u'expires': u'2024-03-19T15:45:00+00:00',
                    u'state': u'pending',
                    u'source': u'plone',
                    u'target': u'recipient',
                    u'source_user': u'regular_user',
                    u'root': u'createtreatydossiers000000000001',
                    u'documents': [u'createtreatydossiers000000000002'],
                    u'participations': [u'p1'],
                    u'all_documents': False,
                    u'all_participations': False,
                }
            ]
        }
        self.assertEqual(expected, browser.json)
